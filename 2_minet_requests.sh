#!/bin/bash

# choose a scientific topic between: "health", "climate" or "COVID-19":
SCIENTIFIC_TOPIC="COVID-19"
CLEAN_DATA_DIRECTORY="clean_data"

INPUT_FILE="./${CLEAN_DATA_DIRECTORY}/fake_url_${SCIENTIFIC_TOPIC}.csv"
OUTPUT_FILE="./${CLEAN_DATA_DIRECTORY}/fake_posts_${SCIENTIFIC_TOPIC}.csv"

token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

if [ ! -f $OUTPUT_FILE ]; 
then
    minet ct summary url $INPUT_FILE --token $token_crowdtangle \
     --posts $OUTPUT_FILE --sort-by total_interactions --start-date 2019-01-01
else
    echo "Nothing to do, the output file already exists"
fi

# The climate command has taken 58 minutes to run on my computer (16 April, 313 URLs).
# The COVID-19 command has taken ? minutes to run on my computer (16 April, 244 URLs).
# The health command has taken ? minutes to run on my computer (16 April, 612 URLs).