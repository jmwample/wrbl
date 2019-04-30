

Install Apt dependencies. 

```
sudo apt install postgresql postgresql-contrib python3-pip python3-tk
```


Activate the python environment and install Python dependencies

```
virtualenv -p /usr/bin/python3.6 .wrbl

source .wrbl/bin/activate

pip install -r requirements.txt
```



Run the App
```
FLASK_APP=app.py

flask run
```


Customize the config (`config.py`)
```
Class YourConfig(BaseConfig):
    API_KEY=XXXXXXXXXXXXXXXXXXXXX
```


### Install grafana 

```
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
curl https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana
sudo service grafana-server start
```

