# AGENTS.md

This repository is designed for long-running coding-agent work. The goal is to
leave the repo in a state where the next session can continue without guessing.

## Project

**VAMPIRE** — Penetration Testing Management System. A Django-based platform for
managing security assessments, vulnerability tracking, SLA compliance, and
report generation (PDF/DOCX).

**Stack:** Django 5.2.3, Python 3.14, SQLite, xhtml2pdf, python-docx,
AdminLTE 3.1 + Bootstrap 4, jQuery 3.7.1

**Pattern:** Function-Based Views (FBV), Django Templates, `@login_required` +
`@permission_required` decorators.

**Apps:** `users`, `organizations`, `projects`, `assignments`, `stakeholders`,
`vkb`, `findings`, `reports`

## Startup Workflow

Before writing code:

1. Confirm the working directory with `pwd`.
2. Read `.specs/project-progress.md` for the latest verified state and next step.
3. Read `.specs/feature_list.json` and choose the highest-priority unfinished feature.
4. Review recent commits with `git log --oneline -5`.
5. Run `./init.sh`.
6. Verify the app starts: `python manage.py runserver` and check `http://127.0.0.1:8000/`

If baseline verification (`./init.sh`) is already failing, fix that first. Do
not stack new feature work on top of a broken starting state.

## Working Rules

- Work on one feature at a time (single active feature).
- Do not mark a feature complete just because code was added.
- Keep changes within the selected feature scope unless a blocker forces a
  narrow supporting fix.
- Do not silently change verification rules during implementation.
- Prefer durable repo artifacts over chat summaries.

## Code Conventions

- **FBV only** — no Class-Based Views.
- **`@login_required`** is mandatory on every view that touches data.
- **`@permission_required`** for views that mutate data.
- **No comments** unless strictly necessary (no docstrings, no inline
  explanations). Code should be self-documenting.
- **Imports**: Django imports first, then third-party, then project imports.
- **URLs**: use `app_name` in urls.py, always use `{% url %}` in templates.
- **Models**: fields ordered: FKs, char fields, text fields, date fields,
  auto-fields.
- **Templates**: extend `base_adminlte.html`, use AdminLTE card/table patterns.
- **Config**: keep sensitive values in settings.py for now (dev project).

## Required Artifacts

- `.specs/feature_list.json`: source of truth for feature state.
- `.specs/project-progress.md`: session log and current verified status.
- `init.sh`: standard startup and verification path.
- `AGENTS.md`: this file.

## Definition Of Done

A feature is done only when all of the following are true:

- The target behavior is implemented.
- The required verification steps (from `feature_list.json`) actually ran and passed.
- Evidence is recorded in `feature_list.json` (`evidence` array) and
  `.specs/project-progress.md`.
- `./init.sh` still passes.
- The repository remains restartable from the standard startup path.

## End Of Session

Before ending a session:

1. Update `.specs/project-progress.md` with what was done, what was verified,
   next step, and any blockers.
2. Update `.specs/feature_list.json` — mark completed features `passing`,
   record evidence, update notes.
3. Record any unresolved risk or blocker in `project-progress.md`.
4. Commit with a descriptive message once the work is in a safe state.
5. Leave the repo clean enough for the next session to run `./init.sh`
   immediately.
