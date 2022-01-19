#!/usr/bin/env bash

python ./server/manage.py migrate
python ./server/manage.py load_fixtures
cd $PWD/server
echo "****"
echo $(ls)
echo "****"
gunicorn /code/server/server.wsgi:application --bind 0.0.0.0:8000 --config /code/server/config/gunnicorn.py
