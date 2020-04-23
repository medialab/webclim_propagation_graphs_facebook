import json
import sys


if __name__ == "__main__":

    if len(sys.argv) == 2:
        if sys.argv[1] in ["COVID-19", "health", "climate", "global"]:
            SCIENTIFIC_TOPIC = sys.argv[1]
        else:
            print("Please enter only 'COVID-19', 'health', 'climate' or 'global' as argument.")
            exit()
    elif len(sys.argv) == 1:
        SCIENTIFIC_TOPIC = "COVID-19"
        print("The topic 'COVID-19' has been chosen by default.")
    else:
        print("Please enter only one argument.")
        exit()

    NODE_COLOR = {
        "climate": "#66F",
        "health": "#FF9",
        "COVID-19": "#F66"
        }

    with open('./bundle/' + SCIENTIFIC_TOPIC.capitalize() + '.json') as input_file:
        graph = json.load(input_file)

    if SCIENTIFIC_TOPIC == "global":
        graph["model"]["nodeAttributes"][2]["modalities"]["climate"]["color"] = NODE_COLOR["climate"]
        graph["model"]["nodeAttributes"][2]["modalities"]["health"]["color"] = NODE_COLOR["health"]
        graph["model"]["nodeAttributes"][2]["modalities"]["covid_19"]["color"] = NODE_COLOR["COVID-19"]
  
    else:
        graph["model"]["nodeAttributes"][0]["modalities"]["facebook_account_or_page"]["color"] = NODE_COLOR[SCIENTIFIC_TOPIC]
        graph["model"]["nodeAttributes"][0]["modalities"]["domain_name"]["color"] = "#999"

    with open('./bundle/' + SCIENTIFIC_TOPIC.capitalize() + '_fixed.json', "w") as output_file:
        json.dump(graph, output_file)

    print("The '{}_fixed.json' bundle has been saved in the 'bundle' folder."\
        .format(SCIENTIFIC_TOPIC.capitalize()))
