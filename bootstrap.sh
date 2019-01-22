#!/bin/sh
export FLASK_APP=./recommend_system/recommend.py
source $(pipenv --venv)/bin/activate
flask run -h 0.0.0.0
