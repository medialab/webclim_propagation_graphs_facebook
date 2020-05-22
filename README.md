# WEBCLIM

WebClim is a research project in Sciences Po's medialab. Our goal is to analyze the fake news ecosystem about climate change, and other scientific topics, on Facebook, Twitter, Youtube, and other platforms. The first results are shown [here](https://medialab.sciencespo.fr/actu/une-cartographie-facebook-des-infox-scientifiques-sur-le-climat/) (in French).

<img src="screenshot_graph.png"/>

### Installations

This project was developed on Python 3.7.6, so you should first install Python. 
Then run these commands in your terminal (in a virtualenv if you prefer):

```
git clone https://github.com/medialab/webclim_analyses
cd webclim_analyses
pip install -r requirements.txt
```
You should export the two following tables in a CSV format from the Science Feedback Airtable database, add the day's date in their name, and put them in the `raw_data` folder:
* "Appearances-Grid view 15_05_2020.csv"
* "Reviews _ Fact-checks-Grid view 15_05_2020.csv"

You should also get a crowdtangle token and write it in a `config.json` file similar to the `config.json.example` file 
(except that you should write the token value instead of "blablabla").

### Run the analysis topic by topic

You can first analyze the Facebook groups sharing fake news about the climate.
First run this command to clean the Science Feedback data:
```
python ./src/clean_data.py climate 15_05_2020
```
The date is used to precise which data you want to clean.

The next command will fetch the Facebook groups having shared the fake news listed by Science Feedback. It should take a certain time to run (1-2 hours):
```
./src/minet_requests.sh climate 15_05_2020
```
Finally you should run this to create the corresponding graph:
```
python ./src/create_topic_graph.py climate 15_05_2020
```
Each command should be run in order because each will use the output of the former as its input.

You can run the same analysis on the fake news about health:
```
python ./src/clean_data.py health 15_05_2020
./src/minet_requests.sh health 15_05_2020
python ./src/create_topic_graph.py health 15_05_2020
```

or about COVID-19:
```
python ./src/clean_data.py COVID-19 15_05_2020
./src/minet_requests.sh COVID-19 15_05_2020
python ./src/create_topic_graph.py COVID-19 15_05_2020
```

### Create a global graph and compare the topics
You can only run this command if you have run all the commands above because we will use their data:
```
python ./src/create_global_graph.py 15_05_2020
```

### Minivan quick hack
This little hack is to manipulate the colors put by minivan when creating the json graph:
```
python ./src/quick_fix_for_minivan_colors.py climate 15_05_2020
```
