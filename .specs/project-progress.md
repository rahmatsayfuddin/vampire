# VAMPIRE — Project Progress

## 2026-07-07 — Tabbed Scanning Reports + Parser Rework

### feat-014: All 7 parsers reworked with real DefectDojo samples
Burp (13/17, host+path), ZAP (42/67, full URI), Nessus (30/288, host:port), Acunetix (18/19), Nmap (host:port)

### feat-015 + feat-016: Tabbed Scanning Reports card
- **Scans tab**: existing scan table (no changes)
- **Trend tab**: tool dropdown + scan checkboxes (Select All/Deselect) + Chart.js stacked bar
- **Compare tab**: dual scan dropdown (tool-filtered) + AJAX compare → 3-column result (New/Recurring/Solved) with Add/FP actions

### feat-017: Project Dashboard (from earlier)
Mini-dashboard on project detail: finding count, late count, SLA%, SPI + severity/SLA doughnut charts

### Verification status
- ./init.sh passes
- 22 tests pass
- E2E: tabs, trend data, compare endpoint all verified
- improve-005: Custom user model (deferred)
