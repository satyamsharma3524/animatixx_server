#!/bin/sh

set -e
python manage.py collectstatic --noinput
sleep 5
python manage.py runserver