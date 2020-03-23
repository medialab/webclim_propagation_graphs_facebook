# WEBCLIM

Our general goal is to better understand the fake news ecosystem: who create the fake news, who share them, etc.

This specific projet maps the Facebook groups sharing fake news URLs, these URLs being extracted from the Science Feedback database.

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
python 1_clean_data.py
```
You should now see a "fake_url.csv" file appear in the `clean_data` folder.

You should now get a crowdtangle token and write it in a `config.json` file similar to the `config.json.example` file 
(except that you should write the token value instead of "blablabla").
The following command will take a long time to run (3 hours on my computer):
```
./2_minet_requests.sh
```
You should now see a "fake_posts.csv" file appear in the `clean_data` folder.

Finally you should run:
```
python 3_create_graphs.py
```
And see the "url_fbgroup_bipartite.gexf" file appear in the `graph` folder.

