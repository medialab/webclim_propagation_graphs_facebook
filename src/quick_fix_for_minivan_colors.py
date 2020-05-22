import json
import sys


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        if sys.argv[1] in ["COVID-19", "health", "climate", "global"]:
            SCIENTIFIC_TOPIC = sys.argv[1]
        else:
            print("Please enter only 'COVID-19', 'health', 'climate' or 'global' as argument.")
            exit()
    else:
        SCIENTIFIC_TOPIC = "COVID-19"
        print("The topic 'COVID-19' has been chosen by default.")

    if len(sys.argv) >= 3:
        DATE = sys.argv[2]
    else:
        DATE = "15_05_2020"
        print("The date '{}' has been chosen by default.".format(DATE))

    NODE_COLOR = {
        "climate": "#66F",
        "health": "#FF9",
        "COVID-19": "#F66"
        }

    with open('./graph/BUNDLE - ' + SCIENTIFIC_TOPIC.capitalize() + ' ' + DATE + '.json') as input_file:
        graph = json.load(input_file)

    if SCIENTIFIC_TOPIC == "global":
        graph["model"]["nodeAttributes"][2]["modalities"]["climate"]["color"] = NODE_COLOR["climate"]
        graph["model"]["nodeAttributes"][2]["modalities"]["health"]["color"] = NODE_COLOR["health"]
        graph["model"]["nodeAttributes"][2]["modalities"]["covid_19"]["color"] = NODE_COLOR["COVID-19"]
  
    else:
        graph["model"]["nodeAttributes"][0]["modalities"]["facebook_account_or_page"]["color"] = NODE_COLOR[SCIENTIFIC_TOPIC]
        graph["model"]["nodeAttributes"][0]["modalities"]["domain_name"]["color"] = "#999"

    with open('./graph/' + SCIENTIFIC_TOPIC + '_' + DATE + '.json', "w") as output_file:
        json.dump(graph, output_file)

    print("The '{}_{}.json' final graph has been saved in the 'graph' folder."\
        .format(SCIENTIFIC_TOPIC, DATE))
