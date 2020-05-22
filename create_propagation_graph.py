import pandas as pd
import networkx as nx


def vizualise_network(claim_beginning):

    sample_url = url_df[url_df["Item reviewed"].str.startswith(claim_beginning)]
    claim = url_df[url_df["Item reviewed"].str.startswith(claim_beginning)]['Item reviewed'].unique()[0]

    sample_posts = posts_df[posts_df["url"].isin(sample_url['url'].unique())]

    G = nx.Graph()
    G.add_node(claim, 
               type="claim",
               importance=5)
    G.add_nodes_from(list(sample_url['url'].unique()), 
                     type="article_or_appearance",
                     importance=2)
    G.add_nodes_from(list(sample_posts['account_name'].unique()), 
                     type="facebook_account_or_page",
                     importance=1)

    G.add_edges_from(list(sample_url[['Item reviewed', 'url']].itertuples(index=False, name=None)))
    G.add_edges_from(list(sample_posts[['account_name', 'url']].itertuples(index=False, name=None)))
    
    return G


if __name__ == "__main__":
    url_df = pd.read_csv("./clean_data/fake_url_COVID-19_20_05_2020.csv")
    posts_df = pd.read_csv("./clean_data/fake_posts_COVID-19_20_05_2020.csv")

    G = vizualise_network("Plandemic")
    nx.write_gexf(G, "./graph/propagation_plandemic.gexf", encoding="utf-8")
    print("The 'propagation_plandemic.gexf' graph has been saved in the 'graph' folder.")
