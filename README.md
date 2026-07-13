# VAMPIRE — Penetration Testing Management System

A Django-based platform for managing security assessments, penetration testing projects, and vulnerability tracking with SLA compliance, audit trails, and Markdown report generation.

## Quick Start

```bash
git clone <repo-url> && cd vampire
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
./init.sh
python manage.py runserver 0.0.0.0:8001
```

Application: `http://127.0.0.1:8001/`

> Port 8001 is used because macOS Docker Desktop occupies port 8000.

## Demo

[https://vampire.rahmatsay.xyz](https://vampire.rahmatsay.xyz)
**Login:** `admin` / `admin123`

## Tech Stack

| Component | Technology |
|---|---|
| Framework | Django 5.2.3 |
| Database | SQLite (dev) / PostgreSQL 16 (Docker) |
| Frontend | AdminLTE 4, Bootstrap 5.3 |
| Charts | Chart.js 4.4, ApexCharts |
| Rich Text | Quill.js 2.0 |
| Select | TomSelect 2.3 |
| Date Picker | flatpickr 4.6 |
| Icons | Bootstrap Icons 1.11 |
| Server | Gunicorn (Docker) |
| Language | Python 3.13 |

## Documentation

- [Setup Guide](docs/setup.md) — prerequisites, install, Docker, baseline checks
- [Architecture](docs/architecture.md) — project structure, services layer, core models
- [Features](docs/features.md) — feature overview by category, SPI + SLA metrics
- [Usage Guide](docs/usage.md) — 12-step walkthrough from organization to report
- [Configuration](docs/configuration.md) — environment variables, settings
- [Development](docs/development.md) — commands, conventions, feature workflow

## License

MIT License. See [LICENSE](LICENSE) file.
