# VAMPIRE — Project Progress

## 2026-07-01 — Session summary

### Completed (14/23 features)

**DevOps (4/4):**
- devops-001: Redefined .gitignore — removed 150 tracked __pycache__, added .env
- devops-002: Dockerize — Dockerfile + docker-compose with PostgreSQL 16
- devops-003: DB migration SQLite → PostgreSQL — env-based config, migrate_db.sh
- devops-004: Default port 8001 — port 8000 occupied by Docker Desktop

**Architecture (2/2):**
- arch-001: Layered architecture assessment — NOT layered, refactor recommended
- arch-002: Refactor to layered — 4 service modules, views are thin HTTP handlers

**Bugs (2/2):**
- bug-001: project_detail empty data — removed unused context, dead org_detail code
- bug-002: Report thread crash — added 'failed' status, styled UI badges

**Features (6/11):**
- feat-001: Dashboard analytics — Chart.js severity/SPI doughnuts, SLA compliance %
- feat-002: Search & filter findings — search bar, severity/status/project/date filters
- feat-006: Audit trail — auto-log create/update/delete for Finding + Project
- feat-007: Report History list page (/reports/) — table with filter dropdowns
- improve-006: MD-based report generation — Markdown template with 7 sections
- improve-007: WYSIWYG PoC editor — django-summernote with image paste/upload

### Active feature
- None

### Next
- tech-001: Unit tests (priority 8)
- feat-003: SLA email notifications (priority 13)
- improve-001: SLA configurable per project (priority 14)
