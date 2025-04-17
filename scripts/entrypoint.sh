#!/bin/sh

set -e
python manage.py collectstatic --noinput
sleep 5
uwsgi --http :80 --master --enable-threads --module animatrixx_server.wsgi --static-map /static=/vol/web/static --buffer-size 36768 --die-on-term
