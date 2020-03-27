#!/bin/bash

minet url-parse --no-strip-protocol url ./clean_data/fake_url.csv > ./clean_data/clean_fake_url.csv

token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

if [ ! -f ./clean_data/fake_posts.csv ]; 
then
    minet ct summary normalized_url ./clean_data/clean_fake_url.csv --token $token_crowdtangle \
     --posts ./clean_data/fake_posts.csv --sort-by total_interactions --start-date 2019-01-01
else
    echo "Nothing to do, the output file already exists"
fi
