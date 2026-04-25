#!/bin/bash
set -e

# Run database migrations
python manage.py migrate --noinput

# Auto-create superuser if environment variables are set
python create_admin.py

# Collect static files
python manage.py collectstatic --noinput

# Start Celery worker in the background
celery -A the_watchtower worker -l info &

# Start Gunicorn server
gunicorn the_watchtower.wsgi:application --bind 0.0.0.0:$PORT
