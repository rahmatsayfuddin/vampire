# Setup Guide

## Prerequisites

- Python 3.8+
- Docker & Docker Compose (for PostgreSQL)

## Local Development

```bash
git clone <repo-url> && cd vampire
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
./init.sh
python manage.py runserver 0.0.0.0:8001
```

Application: `http://127.0.0.1:8001/`

## Docker

```bash
docker compose up --build
```

Includes PostgreSQL 16 with persistent volumes. Application: `http://127.0.0.1:8001/`

## Baseline Checks

```bash
./init.sh               # check + migrate + test (22 tests)
python manage.py test   # run tests directly
```

## Dependencies

```
Django==5.2.3
gunicorn
psycopg2-binary
whitenoise
Pillow
markdown
bleach
lxml
```
