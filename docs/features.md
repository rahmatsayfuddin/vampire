# Features

## Dashboard & Analytics

- Interactive dashboard with Chart.js severity and SPI doughnut charts
- SLA compliance rate with color-coded indicators
- Recent findings and projects tables
- Non-admin users see only assigned project data
- Per-project mini-dashboard (finding count, late count, SLA%, SPI)

## Project Management

- Full lifecycle: Planned → In Progress → Completed → On Hold
- Schedule Performance Index (SPI) — automatic on-time/delayed tracking
- Configurable SLA Profiles per project (Critical/High/Medium/Low)
- Team assignments and stakeholder tracking
- Project notes (logbook) with timestamp

## Findings Management

- Severity levels: Critical (dark), High (red), Medium (yellow), Low (blue)
- SLA tracking with automatic late detection and delay days
- WYSIWYG Proof of Concept (Quill.js) with image upload support
- 3-step creation wizard: VKB template → form → save to VKB
- Advanced search with keyword, severity, status, project, and date range filters
- Pagination with filter-parameter preservation
- Quick actions: close modal + reopen with reason (auto-comment)
- Risk acceptance with SLA override (accept_until)

## Vulnerability Knowledge Base (VKB)

- 8 standard vulnerability categories
- Reusable templates with 3-click import into findings
- Promote custom findings to VKB for future reuse

## Scan Reports

- Upload scan files from 7 tools (Burp, ZAP, Nessus, Acunetix, Nmap, OpenVAS, Generic CSV)
- Auto-detection of multiple formats (Nessus XML v2 + SC CSV)
- Manual parse flow: upload → click Parse → async thread parsing
- Dedicated scan detail page with severity + comparison badges
- Promote parsed findings to tracked Findings, tag as false positive
- Tabbed scanning reports card: Scans list, Trend table, Compare pair
- Compare: select 2 scans → New/Recurring/Solved columns with actions
- Trend: severity count table per scan across tools

## Audit Trail

- Automatic logging of create, update, and delete for Findings and Projects
- Field-level change tracking (e.g. `severity: Medium → High`)
- Activity feed on finding and project detail pages
- Global audit log at `/audit/` (admin only)

## Report Generation

- One-click Markdown report generation (async background thread)
- Live preview of Markdown reports as styled HTML
- Editable report template via admin UI (`/reports/template/`)
- Report history list with project/format/status filters
- Download and delete with responsive action buttons

## Key Metrics

### Schedule Performance Index (SPI)

- `SPI ≥ 1` → On track / ahead of schedule
- `SPI < 1` → Delayed
- Formula: `Planned Duration / Actual Duration`

### SLA Compliance

- Customizable per project via SLA Profiles
- Default: Critical=7d, High=14d, Medium=30d, Low=60d
- Automatic late detection with color-coded indicators
- SLA compliance percentage tracked on dashboard
