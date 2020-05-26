"""Generate a propagation graph with one claim checked by Science Feedback,
all its appearances, and the Facebook groups that have shared at least 
one appearance."""

import sys

import pandas as pd
import networkx as nx


def create_graph(SCIENTIFIC_TOPIC, CLAIM, DATE,
                 CLEAN_DATA_DIRECTORY, GRAPH_DIRECTORY):
    
    url_df = pd.read_csv("./{}/fake_url_{}_{}.csv"\
        .format(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC, DATE))
    sample_url = url_df[url_df["Item reviewed"].str.startswith(CLAIM)]
    claim = url_df[url_df["Item reviewed"].str.startswith(CLAIM)]['Item reviewed'].unique()[0]

    posts_df = pd.read_csv("./{}/fake_posts_{}_{}.csv"\
        .format(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC, DATE))
    sample_posts = posts_df[posts_df["url"].isin(sample_url['url'].unique())]

    G = nx.Graph()

    G.add_node(claim, color="#0F0", type="claim", node_size=20)
    G.add_nodes_from(list(sample_url['url'].unique()), 
                     color="#55F", type="article_or_media", node_size=5)
    G.add_nodes_from(list(sample_posts['account_name'].unique()), 
                     color="#F00", type="facebook_group", node_size=2)

    G.add_edges_from(list(sample_url[['Item reviewed', 'url']].itertuples(index=False, name=None)))
    G.add_edges_from(list(sample_posts[['account_name', 'url']].itertuples(index=False, name=None)))

    nx.write_gexf(G, './{}/{}.gexf'.format(GRAPH_DIRECTORY, CLAIM), encoding="utf-8")


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        if sys.argv[1] in ["COVID-19", "health", "climate"]:
            SCIENTIFIC_TOPIC = sys.argv[1]
        else:
            print("Please enter only 'COVID-19', 'health' or 'climate' as argument.")
            exit()
    else:
        SCIENTIFIC_TOPIC = "COVID-19"
        print("The topic '{}' has been chosen by default.".format(SCIENTIFIC_TOPIC))

    if len(sys.argv) >= 3:
        CLAIM = sys.argv[2]
    else:
        CLAIM = "Plandemic"
        print("The topic '{}' has been chosen by default.".format(CLAIM))

    if len(sys.argv) >= 4:
        DATE = sys.argv[3]
    else:
        DATE = "20_05_2020"
        print("The date '{}' has been chosen by default.".format(DATE))

    CLEAN_DATA_DIRECTORY = "clean_data"
    GRAPH_DIRECTORY = "graph"

    create_graph(SCIENTIFIC_TOPIC, CLAIM, DATE,
                 CLEAN_DATA_DIRECTORY, GRAPH_DIRECTORY)
    print("The '{}.gexf' graph has been saved in the 'graph' folder.".format(CLAIM))
