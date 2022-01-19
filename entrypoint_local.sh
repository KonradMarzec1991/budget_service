#!/bin/sh

python manage.py migrate
python manage.py load_fixtures
python manage.py runserver 0.0.0.0:8000
