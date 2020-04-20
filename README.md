# WEBCLIM

Our general goal is to better understand the fake news ecosystem: who create the fake news, who share them, etc.

This specific projet maps the Facebook groups sharing fake news URLs, these URLs being extracted from the Science Feedback database.

<img src="screenshot_graph.png"/>

### Install the work environment

This project was developed on Python 3.7.6, so you should first install Python. 
Then run these commands in your terminal (in a virtualenv if you prefer):

```
git clone https://github.com/medialab/webclim_analyses
cd webclim_analyses
pip install -r requirements.txt
```

### Run the analyses

Each command should be run in order because each will use the output of the former as its input.

You should first export the two following tables in a CSV format from the Science Feedback database:
* "Appearances-Grid view.csv"
* "Reviews _ Fact-checks-Grid view.csv"

And put them in the `raw_data` folder. Then run this command:
```
python clean_data.py
```
You should now see a "fake_url.csv" file appear in the `clean_data` folder.

You should now get a crowdtangle token and write it in a `config.json` file similar to the `config.json.example` file 
(except that you should write the token value instead of "blablabla").
The following command will take a long time to run (3 hours on my computer):
```
./minet_requests.sh
```
You should now see the "fake_posts.csv" files appear in the `clean_data` folder.

Finally you should run:
```
python create_field_graphs.py
```
You should see a gexf file appear in the `graph` folder. This is the graph for a specific topic.

The command:
```
python create_venn_diagram.py
```
creates two Venn diagrams in png in the `diagram` folder.

