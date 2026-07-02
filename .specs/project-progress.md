# VAMPIRE — Project Progress

## 2026-07-02 — Session summary

### Completed (20/28 features)

**DevOps (4/4):**
- devops-001 to 004: .gitignore, Dockerize, DB migration, port 8001

**Architecture (2/2):**
- arch-001/002: Assessment + refactor to layered services

**Bugs (2/2):**
- bug-001/002: project_detail empty data, report thread crash

**Features:**
- feat-001: Dashboard analytics — Chart.js severity/SPI doughnuts, SLA %
- feat-002: Search & filter findings — q, severity, status, project, date
- feat-006: Audit trail — auto-log create/update/delete for Finding + Project
- feat-007: Report History list page (/reports/) with filter dropdowns
- feat-008: Report Preview — MD rendered as styled HTML in browser
- improve-001: SLA Profiles — configurable per-project SLA templates
- improve-006: MD-based report generation (replaces PDF/DOCX)
- improve-007: WYSIWYG PoC editor → upgraded to Quill.js in ui-002
- improve-008: Edit Template Design — admin UI for MD report template
- tech-001: Unit tests — SLA, SPI, views (22 tests)

**UI Migration (2/5):**
- ui-001: Core Layout v4 — base template + login + sidebar + CDN swap (BS5, no jQuery)
- ui-002: JS Dependencies v4 — TomSelect, flatpickr, Quill.js

### Active feature
- None

### Next
- ui-003: Icons Migration — contextual Bootstrap Icons
- ui-004: Template Porting 1 — findings, projects, organizations
- ui-005: Template Porting 2 — remaining templates
