import pandas as pd
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib_venn import venn3

import networkx as nx
from networkx.algorithms import bipartite

import os
import sys

from create_topic_graph import clean_data


def aggregate_fb_group(fb_group_df_climate, fb_group_df_health, fb_group_df_covid19):

    fb_group_df = fb_group_df_climate.merge(fb_group_df_health,
                                        left_on='account_id', right_on='account_id', 
                                        how='outer', suffixes=('_climate', '_health'))

    fb_group_df = fb_group_df.merge(fb_group_df_covid19,
                                    left_on='account_id', right_on='account_id', 
                                    how='outer')
    fb_group_df = fb_group_df.rename(columns={"account_subscriber_count": "account_subscriber_count_covid",
                                            "nb_fake_news_shared": "nb_fake_news_shared_covid_19",
                                            "account_name": "account_name_covid"})

    fb_group_df["nb_fake_news_climate"]  = fb_group_df["nb_fake_news_shared_climate"].fillna(0).astype(int)
    fb_group_df["nb_fake_news_health"]   = fb_group_df["nb_fake_news_shared_health"].fillna(0).astype(int)
    fb_group_df["nb_fake_news_covid_19"] = fb_group_df["nb_fake_news_shared_covid_19"].fillna(0).astype(int)

    fb_group_df["nb_fake_news"] = (fb_group_df["nb_fake_news_climate"] + 
                                    fb_group_df["nb_fake_news_health"] +
                                    fb_group_df["nb_fake_news_covid_19"])

    fb_group_df['main_topic'] = fb_group_df[["nb_fake_news_climate", 
                                            "nb_fake_news_health", 
                                            "nb_fake_news_covid_19"]].idxmax(axis=1)
    fb_group_df['main_topic'] = fb_group_df['main_topic'].apply(lambda x: x[13:])

    fb_group_df["account_subscriber_count"] = fb_group_df[["account_subscriber_count_climate", 
                                                        "account_subscriber_count_health",
                                                        "account_subscriber_count_covid"]].max(axis=1).astype(int)
                                                        
    fb_group_df['account_name'] = fb_group_df.apply(lambda row: [row['account_name_climate'], 
                                                                row['account_name_health'],
                                                                row['account_name_covid']], axis=1)
    fb_group_df['account_name'] = fb_group_df['account_name'].apply(lambda x: [i for i in x if type(i)==str][0])

    fb_group_df = fb_group_df[["account_id", "account_name", "account_subscriber_count", "main_topic",
                               "nb_fake_news", "nb_fake_news_climate", 
                               "nb_fake_news_health", "nb_fake_news_covid_19"]]
    fb_group_df = fb_group_df.sort_values(by=["main_topic"])
                               
    return fb_group_df


def aggregate_posts(posts_df_climate, posts_df_health, posts_df_covid19):
    posts_df = pd.concat([posts_df_climate, posts_df_health, posts_df_covid19])
    posts_df = posts_df[["account_id", "url"]].drop_duplicates()
    
    posts_df = posts_df.merge(fb_group_df[["account_id", "main_topic"]],
                         on="account_id", how="left")
    posts_df = posts_df.sort_values(by=["main_topic"])
    return posts_df


def color_gradient(ratio_climate, ratio_health, NODE_COLOR):
    """Return an HEX color that is a gradient between three colors, 
    depeding on two ratio values"""
    
    climate_color = np.array(mpl.colors.to_rgb(NODE_COLOR["climate"]))
    health_color = np.array(mpl.colors.to_rgb(NODE_COLOR["health"]))
    covid_color = np.array(mpl.colors.to_rgb(NODE_COLOR["COVID-19"]))

    gradient_color =  (ratio_climate * climate_color + ratio_health * health_color + 
                       (1 - ratio_climate - ratio_health) * covid_color)
    return mpl.colors.to_hex(gradient_color)


def create_global_graph(posts_df, fb_group_df, NODE_COLOR, GRAPH_DIRECTORY, DATE):
    bipartite_graph = nx.Graph()

    for _, row in fb_group_df.iterrows():
        bipartite_graph.add_node(int(row['account_id']),
                                 label=row['account_name'],
                                 nb_fake_news_shared=row['nb_fake_news'],
                                 nb_followers=row['account_subscriber_count'],
                                #  color=color_gradient(row['nb_fake_news_climate']/row['nb_fake_news'], 
                                #                       row['nb_fake_news_health']/row['nb_fake_news'], 
                                #                       NODE_COLOR),
                                #  size=np.sqrt(row['nb_fake_news'])
                                 main_topic=row['main_topic']
                                 )

    bipartite_graph.add_nodes_from(posts_df["url"].tolist())
    
    bipartite_graph.add_edges_from(list(posts_df[['account_id', 'url']]\
                                   .itertuples(index=False, name=None)))

    monopartite_graph = bipartite.projected_graph(bipartite_graph, 
                                                 fb_group_df['account_id'].unique().tolist())

    monopartite_graph_path = os.path.join(".", GRAPH_DIRECTORY, "global_{}.gexf".format(DATE))
    nx.write_gexf(monopartite_graph, monopartite_graph_path, encoding="utf-8")

    return monopartite_graph


def create_venn_diagram(subsets, title, FIGURE_DIRECTORY, DATE):

    plt.figure()

    v = venn3(subsets=subsets, 
              set_labels=('Santé', 'Climat', 'Covid-19'),
              set_colors=([1, 1, 0.6, 1], [0.4, 0.4, 1, 1], [1, 0.4, 0.4, 1]),
              alpha=1)

    v.get_patch_by_id('110').set_color([0.5, 1, 0.5, 1])
    v.get_patch_by_id('101').set_color([1, 0.75, 0.5, 1])
    v.get_patch_by_id('011').set_color([1, 0.4, 1, 1])
    v.get_patch_by_id('111').set_color([0.95, 0.95, 0.95, 1])

    diagram_path = os.path.join(".", FIGURE_DIRECTORY, "venn_diagram_" + title + '_' + DATE + ".png")
    plt.savefig(diagram_path)


def print_statistics(G, fb_group_df, group_subsets):
    centrality = nx.betweenness_centrality(G)
    centrality_df = pd.DataFrame(list(centrality.items()), 
                                 columns = ['account_id', 'betweenness_centrality'])
    centrality_df["account_id"] = centrality_df["account_id"].astype(int)

    fb_group_df = fb_group_df.merge(centrality_df, on="account_id", how="inner")

    generalist_groups = list(group_subsets[0].intersection(group_subsets[1], group_subsets[2]))
    generalist_group_df = fb_group_df[fb_group_df["account_id"].isin(generalist_groups)]
    
    print(generalist_group_df[["account_name", "betweenness_centrality", 
                               "nb_fake_news", "account_subscriber_count"]]\
            .sort_values(by='betweenness_centrality', ascending=False).head(5).to_string(index=False))


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        DATE = sys.argv[1]
    else:
        DATE = "28_04_2020"
        print("The date '{}' has been chosen by default.".format(DATE))

    CLEAN_DATA_DIRECTORY = "clean_data"
    GRAPH_DIRECTORY = "graph"
    FIGURE_DIRECTORY = "figure"

    NODE_COLOR = {
        "climate": "#6666FF",
        "health": "#FFFF66",
        "COVID-19": "#FF6666"
        }

    posts_df_climate, fb_group_df_climate, domain_df_climate = clean_data(CLEAN_DATA_DIRECTORY, "climate", DATE)
    posts_df_health,  fb_group_df_health,  domain_df_health  = clean_data(CLEAN_DATA_DIRECTORY, "health", DATE)
    posts_df_covid19, fb_group_df_covid19, domain_df_covid19 = clean_data(CLEAN_DATA_DIRECTORY, "COVID-19", DATE)

    fb_group_df = aggregate_fb_group(fb_group_df_climate, fb_group_df_health, fb_group_df_covid19)
    posts_df = aggregate_posts(posts_df_climate, posts_df_health, posts_df_covid19)
    G = create_global_graph(posts_df, fb_group_df, NODE_COLOR, GRAPH_DIRECTORY, DATE)
    print("The 'global_{}.gexf' graph has been saved in the 'graph' folder.".format(DATE))

    group_subsets = [
        set(fb_group_df_health['account_id'].values),
        set(fb_group_df_climate['account_id'].values),
        set(fb_group_df_covid19['account_id'].values)
        ]

    create_venn_diagram(group_subsets, "facebook_groups", FIGURE_DIRECTORY, DATE)
    print("The 'venn_diagram_facebook_groups_{}.png' figure has been saved in the 'figure' folder."\
        .format(DATE))

    # selected_groups = fb_group_df[(fb_group_df["nb_fake_news_covid_19"] > 2) &
    #            (fb_group_df["nb_fake_news_climate"] > 2) &
    #            (fb_group_df["nb_fake_news_health"] > 2) &
    #            (fb_group_df["account_subscriber_count"] > 10000)]
    # print(selected_groups.sort_values(by=['account_subscriber_count'], ascending=False)\
    #     [["account_id", "account_name"]].to_string(index=False))

    # print_statistics(G, fb_group_df, group_subsets)

    # group_subsets = [
    #     set(domain_df_climate['domain_name'].values),
    #     set(domain_df_health['domain_name'].values),
    #     set(domain_df_covid19['domain_name'].values)
    #     ]
    # create_venn_diagram(group_subsets, "domain", FIGURE_DIRECTORY, DATE)
    # print("The 'venn_diagram_domain_{}.png' figure has been saved in the 'figure' folder."\
    #     .format(DATE))
    