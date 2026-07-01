#!/bin/sh
set -e

echo "=== VAMPIRE Docker Entrypoint ==="
python manage.py check --deploy --fail-level WARNING 2>/dev/null || python manage.py check
python manage.py migrate
exec gunicorn vampire.wsgi:application --bind 0.0.0.0:8000
