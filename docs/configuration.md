# Configuration

## Environment Variables

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

## Security Headers

Security headers are active when `DEBUG=False`:

- `Strict-Transport-Security` (HSTS): 1 year, include subdomains
- `X-Content-Type-Options`: nosniff
- `X-XSS-Protection`: browser XSS filter
- `SESSION_COOKIE_SECURE` + `CSRF_COOKIE_SECURE`: HTTPS-only cookies

## Logging

Security events (login failures, permission denied, 500 errors) are logged to console via Django's logging framework with `StreamHandler`.
