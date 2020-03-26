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
    posts_df = posts_df[['url', 'account_name', 'account_subscriber_count', 'actual_like_count']]
    posts_df = posts_df.drop_duplicates(subset=['url', 'account_name'], keep='last')

    # We remove the facebook groups that have shared only one fake URL:
    vc = posts_df['account_name'].value_counts()
    posts_df = posts_df[posts_df['account_name'].isin(vc[vc > 1].index)]

    # We merge the two dataframes to get the 'field' column back:
    posts_df = posts_df.merge(clean_url_df[['normalized_url', 'field']], 
                          left_on='url', right_on='normalized_url', how='left')

    # We prepare a dataframe to import the facebook group nodes with specific attributes:
    # - the number of followers -> node size
    # - the ratio of health fake news being shared vs. climate fake news -> node color
    #   (green = a group sharing only fake news about health, blue = only about climate)
    fb_group_df = posts_df.groupby('account_name')['field'].apply(list)\
        .to_frame().reset_index()
    fb_group_df["health_ratio"] = (fb_group_df["field"].apply(lambda x: x.count('health')) /
                                   fb_group_df["field"].apply(len))
    fb_group_df = fb_group_df.merge(posts_df[['account_name', 'account_subscriber_count']].drop_duplicates(),
                                left_on='account_name', right_on='account_name', how='left')

    return posts_df, fb_group_df


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
    (0 = blue, 1 = green)"""
    blue_color = np.array(mpl.colors.to_rgb('#1f77b4'))
    green_color = np.array(mpl.colors.to_rgb('green'))
    return mpl.colors.to_hex((1 - ratio) * blue_color + ratio * green_color)



def create_graphs(posts_df, fb_group_df, GRAPH_DIRECTORY):
    """Create the bipartite graph with the facebook groups and the URLs.
    The edges represent the fact that this group has shared this URL."""
    bipartite_graph = nx.Graph()

    bipartite_graph.add_nodes_from(posts_df['url'].tolist(), 
                                   color="#13ed6a", bipartite=0)

    for _, row in fb_group_df.iterrows():
        bipartite_graph.add_node(row['account_name'], 
                                 color=color_gradient(row['health_ratio']), bipartite=1, 
                                 size=max(min(row['account_subscriber_count'], 5e6)/2e5, 4))

    bipartite_graph.add_edges_from(list(posts_df[['url', 'account_name']].itertuples(index=False, name=None)))

    bipartite_graph_path = os.path.join(".", GRAPH_DIRECTORY, "url_fbgroup_bipartite.gexf")
    nx.write_gexf(bipartite_graph, bipartite_graph_path, encoding="utf-8")

    monopartite_graph = bipartite.projected_graph(bipartite_graph, 
                                                  posts_df['account_name'].tolist())

    monopartite_graph_path = os.path.join(".", GRAPH_DIRECTORY, "fbgroup_monopartite.gexf")
    nx.write_gexf(monopartite_graph, monopartite_graph_path, encoding="utf-8")


if __name__ == "__main__":
    CLEAN_DATA_DIRECTORY = "clean_data"
    GRAPH_DIRECTORY = "graph"

    posts_df, clean_url_df = import_data(CLEAN_DATA_DIRECTORY)
    posts_df, fb_group_df = clean_data(posts_df, clean_url_df)
    print_statistics(posts_df)

    create_graphs(posts_df, fb_group_df, GRAPH_DIRECTORY)
