"""This script is used to clean and gather data 
from the two CSV files extracted from the Science Feedback AirTable"""

import pandas as pd
import os


def import_data(RAW_DATA_DIRECTORY):
    """Import dataframe from the two csv extracted from the 
    Science Feedback AirTable database."""

    url_path = os.path.join(".", RAW_DATA_DIRECTORY, "Appearances-Grid view.csv")
    url_df = pd.read_csv(url_path)

    fact_check_path = os.path.join(".", RAW_DATA_DIRECTORY, "Reviews _ Fact-checks-Grid view.csv")
    fact_check_df = pd.read_csv(fact_check_path)

    return url_df, fact_check_df


def clean_data(url_df):
    """Clean and filter the URL data"""

    # Remove the spaces added by error arount the URLs
    url_df['url'] = url_df['url'].transform(lambda x: x.strip())

    # Remove the URLs that are in double in the dataframe, 
    # keeping only the first, i.e. the more recent ocurrence.
    url_df = url_df.drop_duplicates(subset = "url", keep = "first")

    # Filter the URLs to keep only :
    # 1/ the ones flagged as False
    # 2/ the ones whose fact-check was sent and processed by facebook
    # 3/ the ones that Facebook finally corrected to either "True", "Partly False" and "Not Rated"
    url_df = url_df[(url_df['Flag as'] == 'False') & 
                    (url_df['Fb flagged'] == 'done') &
                    (url_df['Fb correction status'].isna() |
                    (url_df['Fb correction status'] == 'Appeal by publisher'))]

    return url_df


def merge_data(url_df, fact_check_df):
    """Merge the two CSVs to get the fact-check date associated with each URL"""

    url_df = url_df.merge(fact_check_df[['Items reviewed', 'Date of publication']], 
                        left_on='Item reviewed', right_on='Items reviewed', how='left')

    url_df = url_df[['url', 'Item reviewed', 'Date of publication']]

    # One item was not associated with a date, so we remove the corresponding lines
    url_df = url_df.dropna(subset=['Date of publication'])

    return url_df


def save_data(url_df, CLEAN_DATA_DIRECTORY):
    """Save the clean CSV"""
    clean_url_path = os.path.join(".", CLEAN_DATA_DIRECTORY, "fake_url.csv")
    url_df.to_csv(clean_url_path, index=False)


if __name__ == "__main__":

    RAW_DATA_DIRECTORY = "raw_data"
    CLEAN_DATA_DIRECTORY = "clean_data"

    url_df, fact_check_df = import_data(RAW_DATA_DIRECTORY)
    url_df = clean_data(url_df)
    url_df = merge_data(url_df, fact_check_df)
    save_data(url_df, CLEAN_DATA_DIRECTORY)
