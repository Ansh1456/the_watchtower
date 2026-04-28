#!/bin/bash
set -e

# Run database migrations
python manage.py migrate --noinput

# Auto-create superuser if environment variables are set
python create_admin.py

# Collect static files
python manage.py collectstatic --noinput

# NOTE: Celery worker is now a separate Render service (watchtower-celery-worker).
# Do NOT start it here — Render's single-process container will kill it silently.

# Start Gunicorn server
gunicorn the_watchtower.wsgi:application --bind 0.0.0.0:$PORT
