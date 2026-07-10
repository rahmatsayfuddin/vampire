# Architecture

## Pattern

Function-Based Views (FBV) with a services layer. Business logic is extracted from models and views into `services.py` per app. Models only hold field definitions — no business methods.

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
│   ├── parsers.py      # Scan report parsers (7 tools)
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

## Services Layer

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
- **ScanReport** — Uploaded tool scan reports
- **ScanFinding** — Parsed findings from scan reports
- **ProjectNote** — Timestamped project logbook entries
- **ReportHistory** — Generated Markdown report tracking
- **AuditLog** — Auto-logged create/update/delete events
- **ReportTemplate** — Editable MD report template
