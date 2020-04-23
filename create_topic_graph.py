"""Based on which facebook groups have shared the fake news
published by specific domain names,
this script will generate a bipartite graph 
with the facebook groups and the domain names"""

import pandas as pd
import numpy as np
import matplotlib as mpl
import networkx as nx
from networkx.algorithms import bipartite

import os
import sys


def clean_data(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC):
    """Import and prepare the dataframe to be used to build the graphs"""

    posts_path = os.path.join(".", CLEAN_DATA_DIRECTORY, 
                              "fake_posts_" + SCIENTIFIC_TOPIC + ".csv")
    posts_df = pd.read_csv(posts_path)

    clean_url_path = os.path.join(".", CLEAN_DATA_DIRECTORY, 
                                  "fake_url_" + SCIENTIFIC_TOPIC + ".csv")
    clean_url_df = pd.read_csv(clean_url_path)
        
    posts_df = posts_df.dropna(subset=['account_id', 'url'])
    posts_df['account_id'] = posts_df['account_id'].apply(lambda x:int(x))
    
    # Sometimes a same facebook group can share multiple times the same URL, 
    # creating multiple lines in the input CSV. We remove the duplicates here:
    posts_df = posts_df[['url', 'account_name', 'account_id',
                         'account_subscriber_count', 'actual_like_count']]
    posts_df = posts_df.drop_duplicates(subset=['url', 'account_id'], keep='last')
        
    # We remove the facebook groups that have shared only one fake URL:
    vc = posts_df['account_id'].value_counts()
    posts_df = posts_df[posts_df['account_id'].isin(vc[vc > 1].index)]
    
    # We merge the two dataframes to get the 'field' column back:
    posts_df = posts_df.merge(clean_url_df[['url', 'domain_name']], 
                          left_on='url', right_on='url', how='left')

    # Remove the plateforms from the analysis:
    plateforms = ["facebook.com", "youtube.com", "twitter.com", "worpress.com", "instagram.com"]
    posts_df = posts_df[~posts_df['domain_name'].isin(plateforms)]
    
    # We prepare a dataframe to import the facebook group nodes with specific attributes:
    # - the number of followers
    # - the account name -> label
    # - the fake news URL shared by this group -> node size
    fb_group_df = posts_df[['account_id', 'account_name', 'account_subscriber_count']]\
                             .sort_values(by="account_subscriber_count", ascending=True)\
                             .drop_duplicates(subset = ['account_id'], keep='last')

    temp = posts_df.groupby('account_id')['url'].apply(list)\
                .to_frame().reset_index()
    fb_group_df = fb_group_df.merge(temp, left_on='account_id', right_on='account_id', how='left')
    fb_group_df['nb_fake_news_shared'] = fb_group_df['url'].apply(lambda x:len(x))

    # We prepare a dataframe to import the facebook group nodes with specific attributes:
    # - the fake news URL shared by this domain -> node size
    domain_df = clean_url_df.groupby('domain_name')['url'].apply(list)\
                    .to_frame().reset_index()
    domain_df['nb_fake_news_shared'] = domain_df['url'].apply(lambda x:len(x))

    domain_df = domain_df.merge(posts_df[['domain_name']].drop_duplicates(),
                                left_on='domain_name', right_on='domain_name', how='right')
    
    return posts_df, fb_group_df, domain_df


def print_statistics(fb_group_df, domain_df):
    """We print a few interesting statistics"""

    print()
    print("The top 10 of facebook groups sharing the more fake URLs:\n")
    print(fb_group_df[["account_name", "nb_fake_news_shared"]]\
        .sort_values(by='nb_fake_news_shared', ascending=False).head(10).to_string(index=False))

    print()
    print("The top 10 of domains sharing the more fake URLs:\n")
    print(domain_df[["domain_name", "nb_fake_news_shared"]]\
        .sort_values(by='nb_fake_news_shared', ascending=False).head(10).to_string(index=False))

    # print("\n\nThe top 5 of facebook groups with the more followers:\n")
    # temp = posts_df[['account_name', 'account_subscriber_count']].drop_duplicates()
    # print(temp.sort_values(by='account_subscriber_count', ascending=False).head())

    # print("\n\nThe top 5 of facebook groups whose posts get the most cumulated likes:")
    # temp = posts_df[['account_name', 'actual_like_count']].groupby(['account_name']).sum()
    # print(temp.sort_values(by='actual_like_count', ascending=False).head())
    print()


def create_graph(posts_df, fb_group_df, domain_df, 
                 GRAPH_DIRECTORY, SCIENTIFIC_TOPIC):
    """Create the bipartite graph with the facebook groups and the domain names.
    The edges represent the fact that this group has shared the URL coming from this domain."""

    bipartite_graph = nx.Graph()

    for _, row in fb_group_df.iterrows():
        bipartite_graph.add_node(int(row['account_id']),
                                 label=row['account_name'],
                                 type="facebook_account_or_page",
                                 nb_fake_news_shared=row['nb_fake_news_shared'],
                                 nb_followers=row['account_subscriber_count'],
                                 )

    for _, row in domain_df.iterrows():
        bipartite_graph.add_node(row['domain_name'], 
                                 type="domain_name",
                                 nb_fake_news_shared=row['nb_fake_news_shared']
                                 )
    
    bipartite_graph.add_edges_from(list(posts_df[['domain_name', 'account_id']]\
                                   .itertuples(index=False, name=None)))

    bipartite_graph_path = os.path.join(".", GRAPH_DIRECTORY, SCIENTIFIC_TOPIC + ".gexf")
    nx.write_gexf(bipartite_graph, bipartite_graph_path, encoding="utf-8")

    return bipartite_graph


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] in ["COVID-19", "health", "climate"]:
            SCIENTIFIC_TOPIC = sys.argv[1]
        else:
            print("Please enter only 'COVID-19', 'health' or 'climate' as argument.")
            exit()
    elif len(sys.argv) == 1:
        SCIENTIFIC_TOPIC = "COVID-19"
        print("The topic 'COVID-19' has been chosen by default.")
    else:
        print("Please enter only one argument.")
        exit()

    CLEAN_DATA_DIRECTORY = "clean_data"
    GRAPH_DIRECTORY = "graph"

    posts_df, fb_group_df, domain_df = clean_data(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC)

    print_statistics(fb_group_df, domain_df)

    bipartite_graph = create_graph(posts_df, fb_group_df, domain_df, 
                                   GRAPH_DIRECTORY, SCIENTIFIC_TOPIC)
    print("The '{}.gexf' graph has been saved in the 'graph' folder.".format(SCIENTIFIC_TOPIC))
