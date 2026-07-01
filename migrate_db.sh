#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f venv/bin/activate ]; then
    echo "ERROR: venv/ not found. Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

if [ ! -f .env ]; then
    echo "ERROR: .env not found. Copy .env.example to .env and configure PostgreSQL credentials."
    exit 1
fi

export $(grep -v '^#' .env | xargs)

if [ -z "$DB_HOST" ]; then
    echo "ERROR: DB_HOST not set in .env. Set DB_HOST to use PostgreSQL."
    exit 1
fi

echo "=== VAMPIRE SQLite → PostgreSQL Migration ==="

echo "[1/5] Checking PostgreSQL connectivity..."
python -c "
import psycopg2, os
try:
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ.get('DB_PORT', '5432'),
        dbname=os.environ.get('DB_NAME', 'vampire'),
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    conn.close()
    print('PostgreSQL connection OK')
except Exception as e:
    print(f'ERROR: Cannot connect to PostgreSQL: {e}')
    exit(1)
"

echo "[2/5] Dumping SQLite data..."
python manage.py dumpdata \
    --exclude auth.permission \
    --exclude contenttypes \
    --indent 2 \
    > /tmp/vampire_dump.json

echo "[3/5] Running PostgreSQL migrations..."
python manage.py migrate

echo "[4/5] Loading data into PostgreSQL..."
python manage.py loaddata /tmp/vampire_dump.json

echo "[5/5] Cleanup..."
rm -f /tmp/vampire_dump.json

echo "Migration complete. SQLite data is now in PostgreSQL."
echo "You can now remove db.sqlite3 if migration was successful."
