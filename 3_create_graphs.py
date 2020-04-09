"""Based on which facebook groups have shared the fake URLs,
this script is used to generate the summary graphs in .gefx"""

import pandas as pd
import numpy as np
import matplotlib as mpl
import networkx as nx
from networkx.algorithms import bipartite

import os


def import_data(CLEAN_DATA_DIRECTORY):
    """Imports the dataframe created by the minet request"""

    posts_path = os.path.join(".", CLEAN_DATA_DIRECTORY, "fake_posts.csv")
    posts_df = pd.read_csv(posts_path)

    clean_url_path = os.path.join(".", CLEAN_DATA_DIRECTORY, "clean_fake_url.csv")
    clean_url_df = pd.read_csv(clean_url_path)

    return posts_df, clean_url_df


def clean_data(posts_df, clean_url_df):
    """Prepares the dataframe to be used to build the graphs"""

    # Sometimes a same facebook group can share multiple times the same URL, 
    # creating multiple lines in the input CSV. We remove the duplicates here:
    posts_df = posts_df[['url', 'account_name', 'account_id',
                         'account_subscriber_count', 'actual_like_count']]
    posts_df = posts_df.drop_duplicates(subset=['url', 'account_id'], keep='last')

    # We remove the facebook groups that have shared only one fake URL:
    vc = posts_df['account_id'].value_counts()
    posts_df = posts_df[posts_df['account_id'].isin(vc[vc > 1].index)]

    # We merge the two dataframes to get the 'field' column back:
    posts_df = posts_df.merge(clean_url_df[['normalized_url', 'domain_name', 'field']], 
                          left_on='url', right_on='normalized_url', how='left')
    posts_df = posts_df.dropna(subset=['domain_name'])

    # We prepare a dataframe to import the facebook group nodes with specific attributes:
    # - the number of followers -> node size
    # - the ratio of health fake news being shared vs. climate fake news -> node color
    #   (green = a group sharing only fake news about health, blue = only about climate)
    fb_group_df = posts_df.groupby('account_id')['field'].apply(list)\
        .to_frame().reset_index()
    fb_group_df["health_ratio"] = (fb_group_df["field"].apply(lambda x: x.count('health')) /
                                   fb_group_df["field"].apply(len))
    fb_group_df = fb_group_df.merge(posts_df[['account_id', 'account_name', 'account_subscriber_count']]\
                             .sort_values(by="account_subscriber_count", ascending=True)\
                             .drop_duplicates(subset = ['account_id'], keep='last'),
                             left_on='account_id', right_on='account_id', how='left')

    # We prepare a dataframe to import the url nodes with one attribute:
    # - the domain name -> the label
    url_df = posts_df[['url', 'domain_name']].drop_duplicates()

    return posts_df, fb_group_df, url_df


def print_statistics(posts_df):
    """We print a few interesting statistics"""

    print()
    print("The top 5 of facebook groups sharing the more fake URLs:\n")
    print(posts_df['account_name'].value_counts().head())

    print("\n\nThe top 5 of facebook groups with the more followers:\n")
    temp = posts_df[['account_name', 'account_subscriber_count']].drop_duplicates()
    print(temp.sort_values(by='account_subscriber_count', ascending=False).head())

    print("\n\nThe top 5 of facebook groups whose posts get the most cumulated likes:")
    temp = posts_df[['account_name', 'actual_like_count']].groupby(['account_name']).sum()
    print(temp.sort_values(by='actual_like_count', ascending=False).head())
    print()


def color_gradient(ratio):
    """Return an HEX color between green and blue, depeding on the ratio value
    (0 = blue, 1 = yellow)"""
    blue_color = np.array(mpl.colors.to_rgb('#1f77b4'))
    yellow_color = np.array(mpl.colors.to_rgb('#ffea00'))
    return mpl.colors.to_hex((1 - ratio) * blue_color + ratio * yellow_color)


def create_bipartite_graph(posts_df, fb_group_df, url_df, GRAPH_DIRECTORY, graph_option):
    """Create the bipartite graph with the facebook groups and the URLs or domain names.
    The edges represent the fact that this group has shared this URL / domain."""

    bipartite_graph = nx.Graph()

    for _, row in fb_group_df.iterrows():
        bipartite_graph.add_node(row['account_id'],
                                 label=row['account_name'],
                                 type="facebook_account", 
                                 number_followers=np.log10(row['account_subscriber_count']))

    for _, row in url_df.iterrows():
        bipartite_graph.add_node(row[graph_option], 
                                 label=row['domain_name'],
                                 type="domain_name")
    
    bipartite_graph.add_edges_from(list(posts_df[[graph_option, 'account_id']]\
                                   .itertuples(index=False, name=None)))

    bipartite_graph_path = os.path.join(".", GRAPH_DIRECTORY, graph_option + "_fbgroup_bipartite.gexf")
    nx.write_gexf(bipartite_graph, bipartite_graph_path, encoding="utf-8")

    return bipartite_graph


def create_monopartite_graph(bipartite_graph, fb_group_df, GRAPH_DIRECTORY, graph_option):
    """Create the monopartite graph with only the facebook groups."""

    monopartite_graph = bipartite.projected_graph(bipartite_graph, 
                                                  fb_group_df['account_id'].unique().tolist())

    monopartite_graph_path = os.path.join(".", GRAPH_DIRECTORY, graph_option + "_fbgroup_monopartite.gexf")
    nx.write_gexf(monopartite_graph, monopartite_graph_path, encoding="utf-8")


if __name__ == "__main__":
    graph_option = "url" # 2 possibilities: "url" or "domain_name"

    CLEAN_DATA_DIRECTORY = "clean_data"
    GRAPH_DIRECTORY = "graph"

    posts_df, clean_url_df = import_data(CLEAN_DATA_DIRECTORY)
    posts_df, fb_group_df, url_df = clean_data(posts_df, clean_url_df)
    # print_statistics(posts_df)

    bipartite_graph = create_bipartite_graph(posts_df, fb_group_df, url_df, 
                                             GRAPH_DIRECTORY, graph_option)
    create_monopartite_graph(bipartite_graph, fb_group_df, GRAPH_DIRECTORY, graph_option)
