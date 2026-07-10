# Development

## Commands

| Command | Purpose |
|---|---|
| `./init.sh` | Check + migrate + test |
| `python manage.py test` | Run 22 tests |
| `python manage.py runserver 0.0.0.0:8001` | Start dev server |
| `python manage.py makemigrations` | Create migrations |
| `python manage.py migrate` | Apply migrations |
| `python manage.py createsuperuser` | Create admin user |
| `docker compose up --build` | Run with PostgreSQL |

## Code Conventions

See [AGENTS.md](../AGENTS.md) for the full development workflow.

- **FBV only** — no Class-Based Views
- **`@login_required`** mandatory on every view that touches data
- **`@permission_required`** for views that mutate data
- **Services layer** — all business logic in `services.py`, models are field-only
- **No comments** unless strictly necessary — code should be self-documenting
- **Imports**: Django first, then third-party, then project
- **URLs**: use `app_name`, always `{% url %}` in templates
- **Templates**: extend `base_adminlte.html`, AdminLTE card/table patterns
- **Config**: sensitive values in settings.py (dev project)

## Feature Workflow

1. Read `.specs/feature_list.json` — pick highest-priority unfinished feature
2. Read `.specs/project-progress.md` — understand current state
3. Run `./init.sh` to verify baseline
4. Work on ONE feature at a time
5. Do not mark complete until verification steps actually pass
6. Record evidence in `feature_list.json`

## Startup Workflow

1. `pwd` → confirm working directory
2. Read `.specs/project-progress.md`
3. Read `.specs/feature_list.json`
4. `git log --oneline -5`
5. `./init.sh`
6. `python manage.py runserver` → check `http://127.0.0.1:8001/`
