#!/bin/bash

token_crowdtangle=$(jq '.token_crowdtangle' config.json)

if [ ! -f ./clean_data/fake_posts.csv ]; then
    minet ct summary url ./clean_data/fake_url.csv --token $token_crowdtangle \
     --posts ./clean_data/fake_posts.csv --sort-by total_interactions --start-date 2019-01-01
fi
