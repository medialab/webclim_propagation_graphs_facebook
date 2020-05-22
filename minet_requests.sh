#!/bin/bash

if [ $# -ge 1 ] ; then
        if [ $1 = "climate" ] || [ $1 = "health" ] || [ $1 = "COVID-19" ]
        then
                SCIENTIFIC_TOPIC=$1
        else
                echo "Please enter only 'COVID-19', 'health' or 'climate' as argument."
                exit 1
        fi
else
        SCIENTIFIC_TOPIC="COVID-19"
        echo "The topic 'COVID-19' has been chosen by default."
fi

if [ $# -ge 2 ] ; then
        DATE=$2
else
        DATE=$(date +'%d_%m_%Y')
        echo "The topic '${DATE}' has been chosen by default."
fi

CLEAN_DATA_DIRECTORY="clean_data"

INPUT_FILE="./${CLEAN_DATA_DIRECTORY}/fake_url_${SCIENTIFIC_TOPIC}_${DATE}.csv"
OUTPUT_FILE="./${CLEAN_DATA_DIRECTORY}/fake_posts_${SCIENTIFIC_TOPIC}_${DATE}.csv"

token_crowdtangle=$(jq -r '.token_crowdtangle' config.json)

if [ ! -f $OUTPUT_FILE ]; 
then
    minet ct summary url $INPUT_FILE --token $token_crowdtangle \
     --posts $OUTPUT_FILE --sort-by total_interactions --start-date 2019-01-01
else
    echo "Nothing to do, the output file already exists"
fi

## 23 April requests:
# The climate command has taken 47 minutes to run (276 URLs).
# The COVID-19 command has taken 56 minutes to run (328 URLs).
# The health command has taken 1 hour and 52 minutes (676 URLs).

## 15 May requests:
# The climate command has taken 48 minutes (275 URLs).
# The COVID-19 command has taken 1 hour and 12 minutes (432 URLs).
# The health command has taken 1 hour and 42 minutes (613 URLs).
