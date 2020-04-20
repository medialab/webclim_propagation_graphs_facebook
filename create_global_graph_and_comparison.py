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


def create_venn_diagram(subsets, title, FIGURE_DIRECTORY):

    plt.figure()

    v = venn3(subsets=subsets, 
              set_labels=('Climate', 'Health', 'Covid-19'),
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

    specialist = set(fb_group_df_climate['account_id'].values) - \
        set(fb_group_df_health['account_id'].values).union(set(fb_group_df_covid19['account_id'].values))
    specialist_nb = fb_group_df_climate[fb_group_df_climate['account_id'].isin(specialist)]['account_subscriber_count']

    generalist = set(fb_group_df_climate['account_id'].values) - specialist
    generalist_nb = fb_group_df_climate[fb_group_df_climate['account_id'].isin(generalist)]['account_subscriber_count']

    # histogram on log scale, use non-equal bin sizes, such that they look equal on log scale.
    logbins = np.logspace(np.log10(10), np.log10(15000000), 21)

    plt.figure()
    plt.hist(specialist_nb, bins=logbins, color=[0, 0, 1, 0.6], label="Specialist groups")
    plt.hist(generalist_nb, bins=logbins, color=[0.4, 0.4, 0.5, 0.6], label="Generalist groups")
    plt.legend(frameon=False)
    plt.title("Histograms of the number of followers (logarithmic scale)")

    plt.xscale('log')

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

    domain_subsets = [
        set(domain_df_climate['domain_name'].values),
        set(domain_df_health['domain_name'].values),
        set(domain_df_covid19['domain_name'].values)
        ]
    create_venn_diagram(domain_subsets, "domain_names", FIGURE_DIRECTORY)

    compare_follower_number(fb_group_df_climate, fb_group_df_health, 
                            fb_group_df_covid19, FIGURE_DIRECTORY)
