# VAMPIRE - Penetration Testing Management System

A Django-based platform for managing security assessments, penetration testing projects, and vulnerability tracking with SLA compliance, audit trails, and Markdown report generation.

## Overview

VAMPIRE is designed for security teams and penetration testers who need to:
- Manage multiple penetration testing projects
- Track security findings with configurable SLA profiles
- Generate Markdown reports with live preview
- Maintain a reusable vulnerability knowledge base (VKB)
- Monitor project performance with SPI metrics and dashboard analytics

## Features

### Dashboard & Analytics
- Interactive dashboard with Chart.js severity and SPI doughnut charts
- SLA compliance rate with color-coded indicators
- Recent findings and projects tables
- Non-admin users see only assigned project data

### Project Management
- Full lifecycle: Planned → In Progress → Completed → On Hold
- Schedule Performance Index (SPI) — automatic on-time/delayed tracking
- Configurable SLA Profiles per project (Critical/High/Medium/Low)
- Team assignments and stakeholder tracking

### Findings Management
- Severity levels: Critical (dark), High (red), Medium (yellow), Low (blue)
- SLA tracking with automatic late detection and delay days
- WYSIWYG Proof of Concept (Quill.js) with image upload support
- 3-step creation wizard: VKB template → form → save to VKB
- Advanced search with keyword, severity, status, project, and date range filters
- Pagination with filter-parameter preservation

### Vulnerability Knowledge Base (VKB)
- 8 standard vulnerability categories
- Reusable templates with 3-click import into findings
- Promote custom findings to VKB for future reuse

### Audit Trail
- Automatic logging of create, update, and delete for Findings and Projects
- Field-level change tracking (e.g. `severity: Medium → High`)
- Activity feed on finding and project detail pages
- Global audit log at `/audit/` (admin only)

### Report Generation
- One-click Markdown report generation (async background)
- Live preview of Markdown reports as styled HTML
- Editable report template via admin UI (`/reports/template/`)
- Report history list with project/format/status filters
- Download and delete with responsive action buttons

## Tech Stack

| Component | Technology |
|---|---|
| Framework | Django 5.2.3 |
| Database | SQLite (dev) / PostgreSQL 16 (Docker) |
| Frontend | AdminLTE 4, Bootstrap 5.3, Bootstrap Icons |
| Charts | Chart.js 4.4 |
| Rich Text | Quill.js 2.0 (vanilla JS) |
| Select | TomSelect 2.3 (vanilla JS) |
| Date Picker | flatpickr 4.6 |
| Icons | Bootstrap Icons 1.11 |
| Server | Gunicorn (Docker) |
| Language | Python 3.13 |

## Dependencies

```
Django==5.2.3
gunicorn
psycopg2-binary
whitenoise
Pillow
markdown
```

## Quick Start

### Prerequisites
- Python 3.8+
- Docker & Docker Compose (for PostgreSQL)

### Local Development

```bash
git clone <repo-url> && cd vampire
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
./init.sh
python manage.py runserver 0.0.0.0:8001
```

Application: `http://127.0.0.1:8001/`

### Docker

```bash
docker compose up --build
```

Includes PostgreSQL 16 with persistent volumes. Application: `http://127.0.0.1:8001/`

> **Note:** Port 8001 is used because macOS Docker Desktop occupies port 8000.

### Baseline Checks

```bash
./init.sh          # check + migrate + test (22 tests)
python manage.py test    # run tests directly
```

## Project Structure

```
vampire/
├── assignments/        # Team assignment management
├── audit/              # Audit trail (auto-logging)
├── findings/           # Vulnerability findings
│   ├── services.py     # SLA engine + finding lifecycle
│   ├── widgets.py      # Quill.js WYSIWYG widget
│   └── templates/      # Wizard + edit forms
├── menus/              # Menu management
├── organizations/      # Organization (product) management
├── projects/           # Project management
│   ├── services.py     # SPI calculator + project lifecycle
│   └── templates/      # Project forms + SLA profiles
├── reports/            # Markdown report generation
│   ├── services.py     # Report generation + file management
│   └── templates/      # Report list + template editor
├── roles/              # Role-based menu access
├── stakeholders/       # Client contact management
├── users/              # User & group management
├── vkb/                # Vulnerability Knowledge Base
├── vampire/            # Django settings & main URL config
├── templates/          # Base layout + dashboard
├── .specs/             # Feature list + progress tracking
├── init.sh             # Baseline verification script
├── Dockerfile          # Docker build
├── docker-compose.yml  # Docker services
└── requirements.txt    # Python dependencies
```

## Architecture

Function-Based Views (FBV) with a services layer. Business logic is extracted from models and views into `services.py` per app:

| App | Services |
|---|---|
| `findings/` | `SlaService` (SLA engine), `FindingService` (auth, lifecycle, VKB promotion) |
| `projects/` | `ProjectMetricsService` (SPI), `ProjectService` (auth, lifecycle) |
| `organizations/` | `OrganizationService` (user-scoped queries) |
| `reports/` | `ReportService` (file ops), `ReportGenerationService` (async) |

## Core Models

- **Organization** — Products/companies being tested
- **Project** — Pentesting engagements with SPI + SLA profile
- **SlaProfile** — Configurable per-project SLA day templates
- **Finding** — Security vulnerabilities with WYSIWYG PoC
- **VulnerabilityKnowledgeBase** — Reusable vulnerability templates
- **Assignment** — Team member assignments
- **Stakeholder** — Client contacts per project
- **ReportHistory** — Generated Markdown report tracking
- **AuditLog** — Auto-logged create/update/delete events
- **ReportTemplate** — Editable MD report template

## Key Metrics

### Schedule Performance Index (SPI)
- `SPI ≥ 1` → On track / ahead of schedule 🟢
- `SPI < 1` → Delayed 🔴
- Formula: `Planned Duration / Actual Duration`

### SLA Compliance
- Customizable per project via SLA Profiles
- Default: Critical=7d, High=14d, Medium=30d, Low=60d
- Automatic late detection with color-coded indicators
- SLA compliance percentage tracked on dashboard

## Configuration

Key environment variables (via `.env` or Docker Compose):

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(dev only)* | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `ALLOWED_HOSTS` | `*` | Allowed hostnames |
| `DB_HOST` | *(unset = SQLite)* | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `vampire` | Database name |
| `DB_USER` | `vampire` | Database user |
| `DB_PASSWORD` | *(change me)* | Database password |

> When `DB_HOST` is unset, the app uses SQLite for local development.

## Development

| Command | Purpose |
|---|---|
| `./init.sh` | Check + migrate + test |
| `python manage.py test` | Run 22 tests |
| `python manage.py makemigrations` | Create migrations |
| `python manage.py migrate` | Apply migrations |
| `python manage.py createsuperuser` | Create admin user |
| `docker compose up --build` | Run with PostgreSQL |

## Future Enhancements

- [ ] REST API
- [ ] Email SLA notifications
- [ ] CSV/Excel export & import
- [ ] Password reset & rate-limited login
- [ ] Custom user model

## License

MIT License. See LICENSE file.

---

**VAMPIRE** — Penetration Testing Management
