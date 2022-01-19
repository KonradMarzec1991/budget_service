#!/usr/bin/env bash

python ./server/manage.py migrate
python ./server/manage.py load_fixtures
python ./server/manage.py runserver 0.0.0.0:8000
