#!/bin/bash

cd /app

./manage.py migrate
./manage.py stackenadmin

(
    while gunicorn fingerweb.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile - --error-logfile - --capture-output; do
        sleep 10
    done
) &

(
    while nginx; do
        sleep 10
    done
) &

wait
