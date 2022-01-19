#!/bin/sh

python manage.py migrate --no-input
python manage.py load_fixtures
python manage.py collectstatic --no-input

gunicorn server.wsgi:application --bind 0.0.0.0:8000
