#!/bin/bash

if [ $# -eq 1 ] ; then
        if [ $1 = "climate" ] || [ $1 = "health" ] || [ $1 = "COVID-19" ]
        then
                SCIENTIFIC_TOPIC=$1
        else
                echo "Please enter only 'COVID-19', 'health' or 'climate' as argument."
                exit 1
        fi
elif [ $# -eq 0 ]; then
        SCIENTIFIC_TOPIC="COVID-19"
        echo "The topic 'COVID-19' has been chosen by default."
else
        echo "Please enter only one argument."
        exit 1
fi

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
# The COVID-19 command has taken 44 minutes to run on my computer (16 April, 244 URLs).
# The health command has taken 1 hour and 54 minutes to run on my computer (16 April, 612 URLs).