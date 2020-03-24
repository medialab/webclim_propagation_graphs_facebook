"""Based on which facebook groups have shared the fake URLs,
this script is used to generate the summary graphs in .gefx"""

import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite

import os


def import_data(CLEAN_DATA_DIRECTORY):
    """Imports the dataframe created by the minet request"""
    posts_path = os.path.join(".", CLEAN_DATA_DIRECTORY, "fake_posts.csv")
    posts_df = pd.read_csv(posts_path)
    return posts_df


def clean_data(posts_df):
    """Prepares the dataframe to be used to build the graphs"""

    # Sometimes a same facebook group can share multiple times the same URL, 
    # creating multiple lines in the input CSV. We remove the duplicates here:
    posts_df = posts_df[['url', 'account_name', 'account_subscriber_count']]
    posts_df = posts_df.drop_duplicates()

    # We remove the facebook groups that have shared only one fake URL:
    vc = posts_df['account_name'].value_counts()
    posts_df = posts_df[posts_df['account_name'].isin(vc[vc > 1].index)]

    # We print a few interesting statistics:
    print()
    print("The top 5 of facebook groups sharing the more fake URLs:\n")
    print(posts_df['account_name'].value_counts().head())

    print("\n\nThe top 5 of facebook groups with the more followers:\n")
    temp = posts_df[['account_name', 'account_subscriber_count']].drop_duplicates()
    print(temp.sort_values(by="account_subscriber_count", ascending=False).head())
    print()

    return posts_df


def create_bipartite_graph(posts_df, GRAPH_DIRECTORY):
    """Create the bipartite graph with the facebook groups and the URLs.
    The edges represent the fact that this group has shared this URL."""
    G = nx.Graph()

    G.add_nodes_from(posts_df['url'].tolist(), color="#13ed6a", bipartite=0)
    G.add_nodes_from(posts_df['account_name'].tolist(), color="#a84032", bipartite=1)

    G.add_edges_from(list(posts_df[['url', 'account_name']].itertuples(index=False, name=None)))

    graph_path = os.path.join(".", GRAPH_DIRECTORY, "url_fbgroup_bipartite.gexf")
    nx.write_gexf(G, graph_path, encoding="utf-8")


if __name__ == "__main__":
    CLEAN_DATA_DIRECTORY = "clean_data"
    GRAPH_DIRECTORY = "graph"

    posts_df = import_data(CLEAN_DATA_DIRECTORY)
    posts_df = clean_data(posts_df)

    create_bipartite_graph(posts_df, GRAPH_DIRECTORY)
