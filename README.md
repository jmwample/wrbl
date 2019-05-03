
# Wearable Polygraph

## Server and client

[See the writeups on my blog](https://rm-rf-no-preserve.blogspot.com/search/label/WEARABLES).

Install Apt dependencies. 

```
sudo apt install postgresql postgresql-contrib python3-pip python3-tk
```


Activate the python environment and install Python dependencies

```
virtualenv -p /usr/bin/python3.6 .wrbl

source .wrbl/bin/activate

pip3 install -r requirements.txt
```



Run the App
```
FLASK_APP=app.py
FLAS_ENV='production'

python3 app.py
```


Customize the config (`config.py`)
```
Class YourConfig(BaseConfig):
    HOST = '127.0.0.1'
    PORT = 5000
    PSQL_CONN_STR="host='localhost' dbname='wrbl' user='wrbl_data' password='*********'"
    PSQL_ADMIN_CONN_STR="host='localhost' dbname='wrbl' user='wrbl_admin' password='************'"
```

### Install grafana 

```
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
curl https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana
sudo service grafana-server start
```

### TODO FUTURE

Add more sources

Grafana + Experiment Plottiing Fixes

Grafana templating for multiple devices

* https://grafana.com/docs/v3.1/reference/templating/
* https://grafana.com/docs/reference/sharing/
* https://grafana.com/docs/reference/templating/
