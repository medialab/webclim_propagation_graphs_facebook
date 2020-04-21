import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib_venn import venn3

import networkx as nx
from networkx.algorithms import bipartite

import os

from create_field_graph import clean_data


def create_global_graph():
    return {}


#     # We prepare a dataframe to import the facebook group nodes with specific attributes:
#     # - the number of followers -> node size
#     # - the ratio of health fake news being shared vs. climate fake news -> node color
#     #   (green = a group sharing only fake news about health, blue = only about climate)
#     fb_group_df = posts_df.groupby('account_id')['field'].apply(list)\
#         .to_frame().reset_index()
#     fb_group_df["health_ratio"] = (fb_group_df["field"].apply(lambda x: x.count('health')) /
#                                    fb_group_df["field"].apply(len))
#     fb_group_df = fb_group_df.merge(posts_df[['account_id', 'account_name', 'account_subscriber_count']]\
#                              .sort_values(by="account_subscriber_count", ascending=True)\
#                              .drop_duplicates(subset = ['account_id'], keep='last'),
#                              left_on='account_id', right_on='account_id', how='left')


# def color_gradient(ratio):
#     """Return an HEX color between green and blue, depeding on the ratio value
#     (0 = blue, 1 = yellow)"""
#     blue_color = np.array(mpl.colors.to_rgb('#1f77b4'))
#     yellow_color = np.array(mpl.colors.to_rgb('#ffea00'))
#     return mpl.colors.to_hex((1 - ratio) * blue_color + ratio * yellow_color)


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


def compare_follower_number(fb_group_df_climate, fb_group_df_health, 
                            fb_group_df_covid19, FIGURE_DIRECTORY):

    climate = set(fb_group_df_climate['account_id'].values) - \
        set(fb_group_df_health['account_id'].values).union(set(fb_group_df_covid19['account_id'].values))
    climate_nb = fb_group_df_climate[fb_group_df_climate['account_id'].isin(climate)]['account_subscriber_count']
    print("Median follower count for climate only: ", np.median(climate_nb))

    climate_health = set(fb_group_df_climate['account_id'].values) - climate \
        - set(fb_group_df_covid19['account_id'].values)
    climate_health_nb = fb_group_df_climate[fb_group_df_climate['account_id'].isin(climate_health)]['account_subscriber_count']
    print("Median follower count for climate and health: ", np.median(climate_health_nb))

    climate_covid = set(fb_group_df_climate['account_id'].values) - climate \
        - set(fb_group_df_health['account_id'].values)
    climate_covid_nb = fb_group_df_climate[fb_group_df_climate['account_id'].isin(climate_covid)]['account_subscriber_count']
    print("Median follower count for climate and covid: ", np.median(climate_covid_nb))

    climate_health_covid = set(fb_group_df_climate['account_id'].values)\
        .intersection(set(fb_group_df_covid19['account_id'].values), set(fb_group_df_health['account_id'].values))
    climate_health_covid_nb = fb_group_df_climate[fb_group_df_climate['account_id'].isin(climate_health_covid)]['account_subscriber_count']
    print("Median follower count for climate and covid: ", np.median(climate_health_covid_nb))

    plt.figure(figsize=[9, 6])

    plt.plot(np.random.normal(0, 0.04, size=len(climate_health_covid_nb)), climate_health_covid_nb, 
            color='grey', marker='.', linestyle='', alpha=0.5)
    plt.plot([-.2, .2], [np.median(climate_health_covid_nb), np.median(climate_health_covid_nb)],
            color='grey', linestyle='--')

    plt.plot(np.random.normal(1, 0.04, size=len(climate_health_nb)), climate_health_nb, 
            color='green', marker='.', linestyle='', alpha=0.5)
    plt.plot([.8, 1.2], [np.median(climate_health_nb), np.median(climate_health_nb)],
            color='green', linestyle='--')

    plt.plot(np.random.normal(2, 0.04, size=len(climate_covid_nb)), climate_covid_nb, 
            color='violet', marker='.', linestyle='', alpha=0.5)
    plt.plot([1.8, 2.2], [np.median(climate_covid_nb), np.median(climate_covid_nb)],
            color='violet', linestyle='--')

    plt.plot(np.random.normal(3, 0.04, size=len(climate_nb)), climate_nb,
            color='blue', marker='.', linestyle='', alpha=0.5)
    plt.plot([2.8, 3.2], [np.median(climate_nb), np.median(climate_nb)],
            color='blue', linestyle='--')

    plt.yscale('log')

    plt.ylabel("Nombre d'abonnés\n(échelle logarithmique)")
    plt.xticks(np.arange(4), ('Groupes partageant\ndes fake news\nclimat, santé et Covid-19',
                            'Groupes partageant\ndes fake news\nclimat et santé',
                            'Groupes partageant\ndes fake news\nclimat et Covid-19',
                            'Groupes partageant\ndes fake news\nuniquement climat'))
    plt.xlim(-0.5, 3.5)
    plt.tight_layout()

    figure_path = os.path.join(".", FIGURE_DIRECTORY, "comparison_follower_number.png")
    plt.savefig(figure_path)


if __name__ == "__main__":

    CLEAN_DATA_DIRECTORY = "clean_data"
    FIGURE_DIRECTORY = "figure"

    _, fb_group_df_climate, domain_df_climate = clean_data(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC="climate")
    _, fb_group_df_health, domain_df_health   = clean_data(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC="health")
    _, fb_group_df_covid19, domain_df_covid19 = clean_data(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC="COVID-19")

    group_subsets = [
        set(fb_group_df_climate['account_id'].values),
        set(fb_group_df_health['account_id'].values),
        set(fb_group_df_covid19['account_id'].values)
        ]
    create_venn_diagram(group_subsets, "facebook_groups", FIGURE_DIRECTORY)

    # domain_subsets = [
    #     set(domain_df_climate['domain_name'].values),
    #     set(domain_df_health['domain_name'].values),
    #     set(domain_df_covid19['domain_name'].values)
    #     ]
    # create_venn_diagram(domain_subsets, "domain_names", FIGURE_DIRECTORY)

    compare_follower_number(fb_group_df_climate, fb_group_df_health, 
                            fb_group_df_covid19, FIGURE_DIRECTORY)
