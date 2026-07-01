#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== VAMPIRE Startup ==="

if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

echo "[1/2] Django system check..."
python manage.py check
echo "[2/2] Running pending migrations..."
python manage.py migrate

if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

if [ -z "$DB_HOST" ]; then
    echo ""
    echo "⚠ WARNING: Using SQLite. PostgreSQL is recommended for production."
    echo "  Copy .env.example to .env and set DB_HOST to use PostgreSQL."
    echo "  See .env.example for Docker and local PostgreSQL instructions."
    echo ""
fi

echo "Startup OK."
