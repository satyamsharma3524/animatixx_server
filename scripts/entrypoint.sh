#!/bin/sh

set -e
python manage.py collectstatic --noinput
sleep 5
uwsgi --http :8000 --master --enable-threads --module animatrixx_server.wsgi --static-map /static=/vol/web/static --buffer-size 36768 --die-on-term
