# PyTomatoes

PyTomatoes is a python application designed for taking care of plants watering (tomatoes especially) using a Raspberry Pi board. It works by turning on and off a DC water pump according to the schedule that is fetched from the cloud. The app works in the offline-first mode. It caches the schedule in a local SQLite database and uses it if there are connectivity issues.

# Features

* DC water pump control
* fetching the schedule from Firebase real time database
* working in the offline-first mode

# Requirements

You need to have a Firebase account, create a project and set (or put in a file named .env) these environemnt variables:

* API_KEY
* AUTH_DOMAIN
* DATABASE_URL
* STORAGE_BUCKET
* EMAIL
* PASSWORD

Additionaly in the settings you can optionally set:

* local database name - used for caching the schedule
* pin number - responsible for activating the pump through a transistor
* ml per second - determines how much water goes through the pump in a second, this should be measured manually

# Running

Create .env file with required environment variables and then execute in a shell:

```sh
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ sqlite3 db.sqlite3 < db.schema
$ python main.py
```
