# WEBCLIM

[WebClim](https://medialab.sciencespo.fr/activites/webclim/) is a research project in Sciences Po's medialab. Our goal is to analyze the fake news ecosystem about climate change, and other scientific topics, on Facebook, Twitter, Youtube, and other platforms. The first results are shown [here](https://medialab.sciencespo.fr/actu/une-cartographie-facebook-des-infox-scientifiques-sur-le-climat/) and [here](https://medialab.sciencespo.fr/actu/les-infox-sur-le-covid-sous-surveillance/) (in French).

<img src="screenshot_graph.png"/>

### Set up

This project was developed on Python 3.7.6, so you should first install Python. 
Then run these commands in your terminal (in a virtualenv if you prefer):

```
git clone https://github.com/medialab/webclim_propagation_graphs_facebook
cd webclim_analyses
pip install -r requirements.txt
```

### Extract the Science Feedback dataset

You should export the two following tables in a CSV format from the Science Feedback Airtable database, add the day's date in their name, and put them in the `raw_data` folder:
* "Appearances-Grid view 15_05_2020.csv"
* "Reviews _ Fact-checks-Grid view 15_05_2020.csv"

### Collect the CrowdTangle data

You should also get a CrowdTangle token and write it in a `config.json` file similar to the `config.json.example` file 
(except that you should write the token value instead of "blablabla").

You should first clean the Science Feedback data, and then do the CrowdTangle request. For example, if you want the fake news about climate change (the second command will take 1-2 hours to run):
```
python ./src/clean_data.py climate 15_05_2020
./src/minet_requests.sh climate 15_05_2020
```

The same commands can be run with the fake news about health or Covid-19:
```
python ./src/clean_data.py health 15_05_2020
./src/minet_requests.sh health 15_05_2020

python ./src/clean_data.py COVID-19 15_05_2020
./src/minet_requests.sh COVID-19 15_05_2020
```

### Replicate the [first article](https://medialab.sciencespo.fr/actu/une-cartographie-facebook-des-infox-scientifiques-sur-le-climat/)

You can create the climate propagation graph using this command:
```
python ./src/create_topic_graph.py climate 28_04_2020
```
The top 10 Facebook groups and domain names will also be printed by this script.

The second graph with all the Facebook groups sharing scientific fake news can be created by:
```
python ./src/create_global_graph.py 28_04_2020
```
It will also print the top 5 central Facebook groups.

The cluster links matrix can be done with Minivan from the second graph.


### Replicate the [second article](https://medialab.sciencespo.fr/actu/les-infox-sur-le-covid-sous-surveillance/)

The first graph is pretty similar to the climate graph, and can be replicated with the same command:
```
python ./src/create_topic_graph.py COVID-19 20_05_2020
```
This script will also print the top 10 Facebook groups and domain names.

The second graph showing the propagation of the Plandemic movie can be replicated with:
```
python ./src/create_propagation_graph.py COVID-19 Plandemic 20_05_2020
```

The figures showing the temporal evolution of the Facebook groups can be reproduced with [this other GitHub repo](https://github.com/medialab/webclim_temporal_evolution_facebook).

### Minivan quick hack
This little hack is to manipulate the colors displayed by Minivan when creating the json graph:
```
python ./src/quick_fix_for_minivan_colors.py climate 28_04_2020
python ./src/quick_fix_for_minivan_colors.py global 28_04_2020
python ./src/quick_fix_for_minivan_colors.py COVID-19 20_05_2020

```
