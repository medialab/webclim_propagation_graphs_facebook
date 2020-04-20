import json


if __name__ == "__main__":

    # choose a scientific topic between: "health", "climate" or "COVID-19":
    SCIENTIFIC_TOPIC = "climate"
    NODE_COLOR = {
        "climate": "#66F",
        "health": "#FF9",
        "COVID-19": "#F66"
        }

    with open('./bundle/' + SCIENTIFIC_TOPIC.capitalize() + '.json') as input_file:
        graph = json.load(input_file)

    graph["model"]["nodeAttributes"][0]["modalities"]["facebook_account_or_page"]["color"] = NODE_COLOR[SCIENTIFIC_TOPIC]
    graph["model"]["nodeAttributes"][0]["modalities"]["domain_name"]["color"] = "#999"

    with open('./bundle/' + SCIENTIFIC_TOPIC.capitalize() + '_fixed.json', "w") as output_file:
        json.dump(graph, output_file)