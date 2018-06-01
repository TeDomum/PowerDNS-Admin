#!/bin/sh

python create_db.py
gunicorn -t 120 --workers 4 --bind 0.0.0.0:9191 --log-level info app:app

