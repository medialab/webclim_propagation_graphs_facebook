import pandas as pd
import numpy as np

import matplotlib as mpl
from matplotlib_venn import venn3

import networkx as nx
from networkx.algorithms import bipartite

import os

from create_field_graph import clean_data


def create_venn_diagram(subsets, title, DIAGRAM_DIRECTORY):

    mpl.pyplot.figure()

    v = venn3(subsets=subsets, 
              set_labels=('Climate', 'Health', 'Covid-19'),
              set_colors=('b', 'y', 'r'))

    v.get_patch_by_id('110').set_color('green')
    v.get_patch_by_id('011').set_color('orange')
    v.get_patch_by_id('101').set_color('darkviolet')
    v.get_patch_by_id('111').set_color('lightgray')

    diagram_path = os.path.join(".", DIAGRAM_DIRECTORY, "venn_diagram_" + title + ".png")
    mpl.pyplot.savefig(diagram_path)


if __name__ == "__main__":

    CLEAN_DATA_DIRECTORY = "clean_data"
    DIAGRAM_DIRECTORY = "diagram"

    posts_df, fb_group_df_climate, domain_df_climate = clean_data(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC="climate")
    posts_df, fb_group_df_health, domain_df_health = clean_data(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC="health")
    posts_df, fb_group_df_covid19, domain_df_covid19 = clean_data(CLEAN_DATA_DIRECTORY, SCIENTIFIC_TOPIC="COVID-19")

    group_subsets = [
        set(fb_group_df_climate['account_id'].values),
        set(fb_group_df_health['account_id'].values),
        set(fb_group_df_covid19['account_id'].values)
        ]
    create_venn_diagram(group_subsets, "facebook_groups", DIAGRAM_DIRECTORY)

    domain_subsets = [
        set(domain_df_climate['domain_name'].values),
        set(domain_df_health['domain_name'].values),
        set(domain_df_covid19['domain_name'].values)
        ]
    create_venn_diagram(domain_subsets, "domain_names", DIAGRAM_DIRECTORY)

