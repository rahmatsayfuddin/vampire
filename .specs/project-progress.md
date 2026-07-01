# VAMPIRE — Project Progress

## 2026-07-01 — Initial audit and setup

### What was done
- Full codebase audit (models, views, urls, templates, reports architecture).
- Created AGENTS.md, .specs/feature_list.json, .specs/project-progress.md, init.sh.
- 19 features logged in feature_list.json across bug, feat, improve, tech, devops, architecture areas.

### devops-001 — Redefine .gitignore — COMPLETE
- Added standard Python/Django entries: *.so, build artifacts, pytest cache, coverage, translations
- Added .env to gitignore
- Removed duplicate/cruft lines (specific __pycache__ paths already covered by glob)
- Removed 150 tracked __pycache__ files from git index (`git rm --cached`)
- Removed db.sqlite3 from git tracking
- Verified: git check-ignore, untracked-only listing, ./init.sh pass

### devops-002 — Dockerize — COMPLETE
- Dockerfile: python:3.13-slim, gcc + libpq-dev, pip install gunicorn + psycopg2-binary
- docker-compose.yml: web (gunicorn) + db (postgres:16), volumes for postgres_data + media_data
- .env.example: DB config template (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
- .dockerignore: excludes venv, .git, __pycache__, sqlite, media, IDE files
- entrypoint.sh: check + migrate + gunicorn
- settings.py: env-based DATABASES (PostgreSQL when DB_HOST set, SQLite fallback)
- settings.py: SECRET_KEY, DEBUG, ALLOWED_HOSTS from env vars
- Verified: docker compose up --build (image builds, migrations run, gunicorn starts)
- Verified: data persists across down/up cycle (PostgreSQL volume)
- Verified: media files survive restart (media volume mount)
- Verified: ./init.sh works inside container

### devops-003 — Database migration SQLite → PostgreSQL — COMPLETE
- Updated .env.example: Docker + local PostgreSQL documentation with setup steps
- Created migrate_db.sh: dumpdata from SQLite → loaddata to PostgreSQL with connectivity check
- Updated init.sh: SQLite warning banner with link to .env.example
- Added CONN_MAX_AGE=600 to PostgreSQL connection pool settings
- Full integration test on PostgreSQL: Organization, Project, Assignment, Stakeholder, Finding — all CRUD working
- SPI calculation works (SPI=2.01), SLA logic works (Critical=7d, Medium=30d)
- Report generation works on PostgreSQL (PDF generated successfully)
- ./init.sh passes with SQLite fallback (no PostgreSQL required for local dev)

### arch-001 — Layered architecture assessment — COMPLETE
- Audited all 10 models.py: 5 business logic methods (Finding SLA engine, Project SPI)
- Audited all 11 views.py: ~30 business logic violations across 6 view files
- Audited reports/utils.py: monolithic 60-line generate_report_file()
- Identified: 11+ authorization branching duplicates, 4 status lifecycle duplicates, cross-model mutations, raw threading
- 4 apps clean (assignments, stakeholders, menus, users)
- Wrote .specs/architecture-assessment.md with gap analysis, target architecture, 6-phase migration strategy
- Verdict: NOT layered. Refactor IS recommended (arch-002). Start with Phase 1: authorization extraction.

### Observations (audit notes)
- **Bug:** `project_detail` in `projects/views.py:101` passes empty lists for assignments, pics, scans, findings instead of querying them.
- **Bug:** `reports/views.py:run()` has no error handling — thread crashes silently, ReportHistory stuck 'loading'.
- **Bug:** Duplicate `@login_required` decorator at `projects/views.py:75-76`.
- **Bug:** Duplicate `organization_detail` view in `projects/views.py:75` that shadows the real one in `organizations/views.py`.
- **Missing decorators:** `@login_required` missing on stakeholders/, vkb/, menus/, roles/ views.
- **Unused apps:** `menus` and `roles` have models/views but are not in INSTALLED_APPS. Will be discussed separately.
- **Hardcoded values:** SECRET_KEY in settings.py (no env vars), SLA values in Finding model.
- **No tests:** All tests.py files are empty placeholders.
- **Reports:** PDF and DOCX paths share zero code. `reports/sections/` has 7 empty stubs, only methodology.py is implemented.

### Notes
- **Reporting strategy change**: improve-006 added — switch to Markdown-based reports (MD as primary output, optional PDF conversion). Supersedes improve-003 (unified PDF/DOCX pipeline) and improve-004 (DOCX section stubs). Remove xhtml2pdf + python-docx dependencies, keep only Markdown rendering.

### arch-002 — Refactor to layered architecture — COMPLETE
- Created 4 service modules: findings/services.py, projects/services.py, organizations/services.py, reports/services.py
- findings/services.py: SlaService (4 methods) + FindingService (4 methods) — extracted SLA engine and auth branching
- projects/services.py: ProjectMetricsService.spi() + ProjectService (3 methods) — extracted SPI formula and auth branching
- organizations/services.py: OrganizationService.get_queryset_for_user()
- reports/services.py: ReportService (4 methods) + ReportGenerationService (3 methods) — extracted MIME mapping, file I/O, threading, added error handling
- Models: Finding SLA methods and Project.spi() delegate to services (backward compatible with templates)
- Views refactored: all 4 view files now call services instead of inline business logic
- Removed: 11+ authorization branching duplicates, 4 status lifecycle duplicates, duplicate @login_required, duplicate organization_detail comments, raw threading from views
- Smoke tested: SLA, SPI, lifecycle (close/reopen), VKB promotion, report generation — all pass
- ./init.sh passes

### Active feature
- None (setup session)

---
