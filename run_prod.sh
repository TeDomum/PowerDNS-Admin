#!/bin/sh

python manage.py create_db
gunicorn -t 120 --workers 4 --bind 0.0.0.0:9191 --log-level info app:app

