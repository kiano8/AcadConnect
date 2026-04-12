#!/bin/bash
set -e

export DJANGO_SETTINGS_MODULE=config.settings

echo "Installing dependencies..."
python3 -m pip install --break-system-packages -r requirements.txt

echo "Running database migrations..."
python3 manage.py migrate --noinput

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

