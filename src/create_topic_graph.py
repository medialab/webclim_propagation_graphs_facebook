"""Based on which facebook groups have shared the fake news
published by specific domain names,
this script will generate a bipartite graph 
with the facebook groups and the domain names"""

import pandas as pd
import numpy as np
import matplotlib as mpl
import networkx as nx
from networkx.algorithms import bipartite
import ural

import os
import sys


def clean_data(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC, DATE):
    """Import and prepare the dataframe to be used to build the graphs"""

    posts_path = os.path.join(".", CLEAN_DATA_DIRECTORY, 
                              "fake_posts_" + SCIENTIFIC_TOPIC + "_" + DATE + ".csv")
    posts_df = pd.read_csv(posts_path)
        
    posts_df = posts_df[posts_df["platform"] == "Facebook"]
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

    posts_df['domain_name'] = posts_df['url'].apply(lambda x: ural.get_domain_name(x))

    # # Remove the plateforms from the analysis:
    # plateforms = ["facebook.com", "youtube.com", "twitter.com", "wordpress.com", "instagram.com"]
    # posts_df = posts_df[~posts_df['domain_name'].isin(plateforms)]

    # # Remove the url with parameters from the analysis because CT return wrong results for them:
    # posts_df['parameter_in_url'] = posts_df['url'].apply(lambda x: '?' in x)
    # posts_df = posts_df[posts_df['parameter_in_url']==False]
    
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
    domain_df = posts_df[['url', 'domain_name']].drop_duplicates()\
                    .groupby('domain_name')['url'].apply(list)\
                    .to_frame().reset_index()
    domain_df['nb_fake_news_shared'] = domain_df['url'].apply(lambda x:len(x))
    
    return posts_df, fb_group_df, domain_df


def print_statistics(fb_group_df, domain_df):
    """We print a few interesting statistics"""

    print()
    print("The top 10 of facebook groups sharing the more fake URLs:\n")
    print(fb_group_df[["account_name", "nb_fake_news_shared", "account_subscriber_count"]]\
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
                 GRAPH_DIRECTORY, SCIENTIFIC_TOPIC, DATE):
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

    bipartite_graph_path = os.path.join(".", GRAPH_DIRECTORY, SCIENTIFIC_TOPIC + "_" + DATE + ".gexf")
    nx.write_gexf(bipartite_graph, bipartite_graph_path, encoding="utf-8")

    return bipartite_graph


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        if sys.argv[1] in ["COVID-19", "health", "climate"]:
            SCIENTIFIC_TOPIC = sys.argv[1]
        else:
            print("Please enter only 'COVID-19', 'health' or 'climate' as argument.")
            exit()
    else:
        SCIENTIFIC_TOPIC = "COVID-19"
        print("The topic 'COVID-19' has been chosen by default.")

    if len(sys.argv) >= 3:
        DATE = sys.argv[2]
    else:
        DATE = "20_05_2020"
        print("The date '{}' has been chosen by default.".format(DATE))

    CLEAN_DATA_DIRECTORY = "clean_data"
    GRAPH_DIRECTORY = "graph"

    posts_df, fb_group_df, domain_df = clean_data(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC, DATE)

    print_statistics(fb_group_df, domain_df)

    bipartite_graph = create_graph(posts_df, fb_group_df, domain_df, 
                                   GRAPH_DIRECTORY, SCIENTIFIC_TOPIC, DATE)
    print("The '{}_{}.gexf' graph has been saved in the 'graph' folder.".format(SCIENTIFIC_TOPIC, DATE))
