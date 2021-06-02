# PyTomatoes

PyTomatoes is a python application designed for taking care of plants watering (tomatoes especially) using a Raspberry Pi board. It works by turning on and off a DC water pump according to the schedule that is fetched from the cloud. The app works in the offline-first mode. It caches the schedule in a local SQLite database and uses it if there are connectivity issues.

# Features

* DC water pump control
* fetching the schedule from the backend
* working in the offline-first mode

# Requirements

Add these variables to configure hardware details:

* EMAIL - account email address
* PASSWORD - account password
* DB_NAME - local database name
* PIN - pin responsible for activating the pump through a transistor
* ML_PER_SECOND - determines how much water goes through the pump in a second, this should be measured manually

# Running

1. Create .env file with required environment variables
2. Create a schedule in the backend using admin panel
3. Execute in a shell:

```sh
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ sqlite3 db.sqlite3 < db.schema
$ python main.py
```
