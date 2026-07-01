# VAMPIRE — Project Progress

## 2026-07-01 — Initial audit and setup

### What was done
- Full codebase audit (models, views, urls, templates, reports architecture).
- Created AGENTS.md, .specs/feature_list.json, .specs/project-progress.md, init.sh.
- 19 features logged in feature_list.json across bug, feat, improve, tech, devops, architecture areas.
- Added 3 devops features: redefined .gitignore (devops-001), Dockerize (devops-002), database migration SQLite→PostgreSQL (devops-003).
- Added 2 architecture features: layered architecture assessment (arch-001), refactor to layered (arch-002).

### devops-001 — Redefine .gitignore — COMPLETE
- Added standard Python/Django entries: *.so, build artifacts, pytest cache, coverage, translations
- Added .env to gitignore
- Removed duplicate/cruft lines (specific __pycache__ paths already covered by glob)
- Removed 150 tracked __pycache__ files from git index (`git rm --cached`)
- Removed db.sqlite3 from git tracking
- Verified: git check-ignore, untracked-only listing, ./init.sh pass

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
