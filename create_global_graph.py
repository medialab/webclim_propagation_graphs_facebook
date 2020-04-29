import pandas as pd
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib_venn import venn3

import networkx as nx
from networkx.algorithms import bipartite

import os
import sys
import time

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

    fb_group_df["nb_fake_news_shared"] = (fb_group_df["nb_fake_news_shared_climate"].fillna(0).astype(int) + 
                                        fb_group_df["nb_fake_news_shared_health"].fillna(0).astype(int) +
                                        fb_group_df["nb_fake_news_shared_covid_19"].fillna(0).astype(int))

    fb_group_df["ratio_climate"] = (fb_group_df["nb_fake_news_shared_climate"].fillna(0).astype(int) /
                                    fb_group_df["nb_fake_news_shared"])

    fb_group_df["ratio_health"] = (fb_group_df["nb_fake_news_shared_health"].fillna(0).astype(int) /
                                    fb_group_df["nb_fake_news_shared"])

    # fb_group_df['main_topic'] = fb_group_df[["nb_fake_news_shared_climate", 
    #                                         "nb_fake_news_shared_health", 
    #                                         "nb_fake_news_shared_covid_19"]].idxmax(axis=1)
    # fb_group_df['main_topic'] = fb_group_df['main_topic'].apply(lambda x: x[20:])

    fb_group_df["account_subscriber_count"] = fb_group_df[["account_subscriber_count_climate", 
                                                        "account_subscriber_count_health",
                                                        "account_subscriber_count_covid"]].max(axis=1).astype(int)
                                                        
    fb_group_df['account_name'] = fb_group_df.apply(lambda row: [row['account_name_climate'], 
                                                                row['account_name_health'],
                                                                row['account_name_covid']], axis=1)
    fb_group_df['account_name'] = fb_group_df['account_name'].apply(lambda x: [i for i in x if type(i)==str][0])

    # fb_group_df = fb_group_df[["account_id", "account_name", "account_subscriber_count",
    #                            "nb_fake_news_shared", "main_topic"]]

    fb_group_df = fb_group_df[["account_id", "account_name", "account_subscriber_count",
                               "nb_fake_news_shared", "ratio_climate", "ratio_health"]]
                               
    return fb_group_df


def aggregate_posts(posts_df_climate, posts_df_health, posts_df_covid19):
    posts_df = pd.concat([posts_df_climate, posts_df_health, posts_df_covid19])
    posts_df = posts_df[["account_id", "url"]].drop_duplicates()
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
                                 nb_fake_news_shared=row['nb_fake_news_shared'],
                                 nb_followers=row['account_subscriber_count'],
                                 color=color_gradient(row['ratio_climate'], 
                                                      row['ratio_health'], NODE_COLOR),
                                 size=np.sqrt(row['nb_fake_news_shared'])
                                #  main_topic=row['main_topic']
                                 )

    bipartite_graph.add_nodes_from(posts_df["url"].tolist())
    
    bipartite_graph.add_edges_from(list(posts_df[['account_id', 'url']]\
                                   .itertuples(index=False, name=None)))

    monopartite_graph = bipartite.projected_graph(bipartite_graph, 
                                                 fb_group_df['account_id'].unique().tolist())

    monopartite_graph_path = os.path.join(".", GRAPH_DIRECTORY, "global_{}.gexf".format(DATE))
    nx.write_gexf(monopartite_graph, monopartite_graph_path, encoding="utf-8")


def create_venn_diagram(subsets, title, FIGURE_DIRECTORY):

    plt.figure()

    v = venn3(subsets=subsets, 
              set_labels=('Climat', 'Santé', 'Covid-19'),
              set_colors=([0.4, 0.4, 1, 1], [1, 1, 0.6, 1], [1, 0.4, 0.4, 1]),
              alpha=1)

    v.get_patch_by_id('110').set_color([0.5, 1, 0.5, 1])
    v.get_patch_by_id('011').set_color([1, 0.75, 0.5, 1])
    v.get_patch_by_id('101').set_color([1, 0.4, 1, 1])
    v.get_patch_by_id('111').set_color([0.95, 0.95, 0.95, 1])

    diagram_path = os.path.join(".", FIGURE_DIRECTORY, "venn_diagram_" + title + ".png")
    plt.savefig(diagram_path)


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        DATE = sys.argv[1]
    else:
        DATE = time.strftime("%d,%m,%Y").replace(",", "_")
        print("The date '{}' has been chosen by default.".format(DATE))

    CLEAN_DATA_DIRECTORY = "clean_data"
    GRAPH_DIRECTORY = "graph"
    FIGURE_DIRECTORY = "figure"

    NODE_COLOR = {
        "climate": "#6666FF",
        "health": "#FFFF66",
        "COVID-19": "#FF6666"
        }

    posts_df_climate, fb_group_df_climate, _ = clean_data(CLEAN_DATA_DIRECTORY, "climate", DATE)
    posts_df_health,  fb_group_df_health, _  = clean_data(CLEAN_DATA_DIRECTORY, "health", DATE)
    posts_df_covid19, fb_group_df_covid19, _ = clean_data(CLEAN_DATA_DIRECTORY, "COVID-19", DATE)

    fb_group_df = aggregate_fb_group(fb_group_df_climate, fb_group_df_health, fb_group_df_covid19)
    posts_df = aggregate_posts(posts_df_climate, posts_df_health, posts_df_covid19)
    create_global_graph(posts_df, fb_group_df, NODE_COLOR, GRAPH_DIRECTORY, DATE)
    print("The 'global_{}.gexf' graph has been saved in the 'graph' folder.".format(DATE))

    group_subsets = [
        set(fb_group_df_climate['account_id'].values),
        set(fb_group_df_health['account_id'].values),
        set(fb_group_df_covid19['account_id'].values)
        ]
    create_venn_diagram(group_subsets, "facebook_groups", FIGURE_DIRECTORY)
    print("The 'venn_diagram_facebook_groups.png' figure has been saved in the 'figure' folder.")

    generalist_groups = list(group_subsets[0].intersection(group_subsets[1], group_subsets[2]))
    print(fb_group_df_climate[["account_id", "account_name", "account_subscriber_count"]]\
            [fb_group_df_climate["account_id"].isin(generalist_groups)]\
            .sort_values(by='account_subscriber_count', ascending=False).head(10))

