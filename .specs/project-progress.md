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

### Next step
- bug-001 (priority 1): Fix project_detail to query actual assignments, findings, and reports.

### Active feature
- None (setup session)

---
