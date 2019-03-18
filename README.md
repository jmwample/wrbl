

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
