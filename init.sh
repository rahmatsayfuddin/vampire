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
echo "Startup OK."
