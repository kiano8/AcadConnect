#!/bin/bash
set -e

echo "Installing dependencies..."
python3 -m pip install --break-system-packages -r requirements.txt

echo "Collecting static files..."
export DJANGO_SETTINGS_MODULE=config.settings
python3 manage.py collectstatic --noinput
