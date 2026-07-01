# VAMPIRE — Architecture Assessment: Layered Architecture

Date: 2026-07-01

## Verdict: NOT layered

VAMPIRE is a **flat Django FBV project** with no service layer. Business logic is
scattered across models, views, and a monolithic utility function. There is no
separation between HTTP handling, business rules, and data access.

---

## 1. Current Architecture

```
┌─────────────────────────────────────────────┐
│  HTTP Layer (views.py)                       │
│  ┌─────────────────────────────────────────┐│
│  │ • Request parsing                        ││
│  │ • Permission checks (@login_required)    ││
│  │ • Authorization branching (superuser?)   ││ ← repeated 11+ times
│  │ • Direct ORM queries                     ││
│  │ • Business rules (closed_at, completed)  ││ ← duplicated across views
│  │ • Cross-model creation (VKB promotion)   ││
│  │ • Thread spawning (report generation)    ││
│  │ • File I/O (os.remove, os.path.exists)   ││
│  │ • Template rendering                     ││
│  └─────────────────────────────────────────┘│
│             │                                │
│  ┌──────────▼──────────────────────────────┐│
│  │  Model Layer (models.py)                 ││
│  │  • Field definitions                     ││
│  │  • SLA engine (Finding.sla_days, etc.)   ││ ← hardcoded rules
│  │  • SPI formula (Project.spi)             ││
│  │  • __str__                               ││
│  └─────────────────────────────────────────┘│
│             │                                │
│  ┌──────────▼──────────────────────────────┐│
│  │  Utils (reports/utils.py)                 ││
│  │  • Report HTML rendering                 ││
│  │  • PDF generation (xhtml2pdf)            ││
│  │  • DOCX assembly (python-docx)           ││
│  │  • File I/O (mkdir, write)               ││
│  │  • Filename generation                   ││
│  └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

## 2. Business Logic Inventory

### 2.1 In models.py (methods on model classes)

| Location | Method | Problem |
|---|---|---|
| `findings/models.py:39` | `Finding.sla_days()` | SLA severity→days mapping is hardcoded dict, unconfigurable |
| `findings/models.py:47` | `Finding.sla_due_date()` | Date arithmetic using timezone.now() — not testable with date injection |
| `findings/models.py:50` | `Finding.is_late()` | Conditional logic branches on status + date comparison |
| `findings/models.py:57` | `Finding.sla_delay_days()` | Overdue-day calculation with max() floor |
| `projects/models.py:24` | `Project.spi()` | SPI formula with 3 edge cases and date fallback logic |

**5 methods, 2 models.** These are "active record" anti-pattern — models should be
data containers, not computation engines.

### 2.2 In views.py (mixed with HTTP handling)

| View File | Code | Issue |
|---|---|---|
| `findings/views.py:14-17` | `if user.is_superuser: all()` else `filter(assignment__user=...)` | Authorization branching repeated 10+ times across 3 view files |
| `findings/views.py:46-49` | `if status=='Closed': set closed_at` else `clear closed_at` | Finding lifecycle rule duplicated in create + edit |
| `findings/views.py:53-61` | `if save_to_vkb: VulnerabilityKnowledgeBase.objects.create(...)` | Cross-model creation in a view |
| `projects/views.py:25-28` | `if status=='Completed': set completed_date` else `clear it` | Project lifecycle rule duplicated in create + update |
| `projects/views.py:75-94` | `organization_detail` in projects/views.py | **Duplicate view** — also exists in organizations/views.py |
| `reports/views.py:19-28` | `threading.Thread(target=run, args=...).start()` | Thread spawning + history creation in a view |
| `reports/views.py:31-42` | `run()` at module level | Business logic defined as free function in views.py |
| `reports/views.py:51-54` | Format→MIME mapping inline | Domain mapping in HTTP handler |
| `reports/views.py:70-77` | `os.path.join(...) + os.remove(...) + .delete()` | File I/O and DB deletion in a view |

**~30 instances of business logic across 6 view files.**

### 2.3 In utils.py

| Location | Line Count | Problem |
|---|---|---|
| `reports/utils.py:generate_report_file()` | ~60 lines | Monolithic function: renders templates, generates PDF via xhtml2pdf, assembles DOCX via python-docx, does file I/O, generates filenames, dispatches by format string. Zero separation between PDF and DOCX paths. |

### 2.4 Apps with zero business logic

These 4 apps are "thin" — views only do form handling and redirects:

| App | Verdict |
|---|---|
| `assignments/` | Clean. Only form-based CRUD. |
| `stakeholders/` | Clean. Only form-based CRUD. |
| `menus/` | Clean. Only form-based CRUD. |
| `users/` | Clean. Delegates to Django's built-in User model. |

---

## 3. Top Problems

### 3.1 Authorization branching — 11+ duplicates

```python
# Repeated verbatim in finding_list, create_finding, finding_detail,
# edit_finding, delete_finding, project_list, project_update, project_delete,
# project_detail, organization_list, organization_detail
if request.user.is_superuser:
    queryset = Model.objects.all()
else:
    queryset = Model.objects.filter(...assignment__user=request.user).distinct()
```

**Risk:** Changing the authorization rule (e.g., adding a "Manager" group bypass)
requires editing 11+ locations.

### 3.2 Status lifecycle rules — duplicated create/edit pairs

Both `Finding.closed_at` and `Project.completed_date` have identical
"set-on-complete, clear-on-reopen" logic duplicated across create and update
views (4 occurrences total).

```python
# findings/views.py — lines 46-49 AND lines 90-93
if finding.status == 'Closed' and not finding.closed_at:
    finding.closed_at = timezone.now()
elif finding.status != 'Closed':
    finding.closed_at = None
```

**Risk:** Updating the rule in one place leaves the other stale.

### 3.3 Report generation — worst offender

`reports/views.py:31-42` defines `run()` as a module-level function that:
1. Fetches a ReportHistory record
2. Queries findings
3. Calls `generate_report_file()` (which is itself 60 lines of mixed concerns)
4. Updates ReportHistory status

This function is called from a `threading.Thread` spawned in the view. There is
zero error handling — thread crashes are silently lost (ReportHistory stuck 'loading').

### 3.4 Duplicate organization_detail view

`projects/views.py:75` contains a copy of `organization_detail` that shadows the
original in `organizations/views.py:49`. Both contain slightly divergent logic.

---

## 4. Target Architecture

```
┌──────────────────────────────────────────────────────┐
│  HTTP Layer (views.py)                                │
│  • Request parsing / form validation                   │
│  • Permission checks (@login_required)                 │
│  ★ Calls service functions, NOT ORM directly           │
└──────────────┬───────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────┐
│  Service Layer (services.py per app)                  │
│  • Authorization: get_queryset_for_user(user)         │
│  • Business rules: SLA engine, SPI calculator         │
│  • Lifecycle: close_finding(), reopen_finding()       │
│  • Cross-model: promote_to_vkb()                      │
│  • Orchestration: generate_report_async()             │
│  • All ORM access encapsulated here                   │
└──────────────┬───────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────┐
│  Data Layer (models.py)                                │
│  • Fields + relationships only                         │
│  • __str__ only                                        │
│  • No business methods                                │
└──────────────────────────────────────────────────────┘
```

### Target structure per app

```
findings/
├── models.py        ← fields only
├── services.py      ← FindingService, SlaService
├── views.py         ← thin HTTP handlers
├── forms.py
├── urls.py

projects/
├── models.py        ← fields only
├── services.py      ← ProjectService, ProjectMetricsService
├── views.py
├── forms.py
├── urls.py

reports/
├── models.py
├── services.py      ← ReportGenerationService, ReportFileService
├── views.py
├── sections/        ← content builders (already modular)
├── utils.py         ← PDF/DOCX renderers (infrastructure, not business logic)
├── urls.py
```

For apps with no business logic (`assignments`, `stakeholders`, `menus`, `users`),
services.py is optional — their views can keep direct ORM since there's no
logic to extract.

---

## 5. Migration Strategy (Incremental)

Do NOT rewrite everything at once. Extract services incrementally:

| Phase | Scope | Effort |
|---|---|---|
| **Phase 1**: Authorization | Create `get_queryset_for_user(user, model)` in each service, replace 11+ branches | Small, high impact |
| **Phase 2**: Findings SLA | Extract `SlaService` from `Finding` model methods, update views | Medium |
| **Phase 3**: Project metrics | Extract `ProjectMetricsService.spi()` from `Project.spi()` | Small |
| **Phase 4**: Status lifecycle | Extract `set_closed_at_by_status()` into services, remove 4 duplicates | Small |
| **Phase 5**: Report generation | Move `run()` + `generate_report_file()` into `ReportGenerationService` | Large |
| **Phase 6**: Cross-model ops | Extract VKB promotion, role menu sync into services | Medium |

---

## 6. Recommendation

**Refactor to layered architecture IS recommended** (arch-002).
The project is small enough (~2000 lines) that a refactor is manageable, but
the accumulation of business logic in views/models is already causing
duplication and will accelerate as more features are added.

Start with Phase 1 (authorization) — it is the highest-duplication, lowest-risk
change, and will immediately reduce ~30 lines of repeated code across 11 locations.

Do NOT introduce a repository pattern — Django's ORM is already a sufficient
data-access abstraction. The service layer should encapsulate business rules
and orchestration, not re-wrap the ORM.

---

## Appendix: Complete Violation List

### findings/views.py
| Line(s) | Function | Violation |
|---|---|---|
| 14-17 | `finding_list` | Authorization branching |
| 31-34 | `create_finding` | Authorization branching |
| 42-44 | `create_finding` | Conditional VKB reference linking |
| 46-49 | `create_finding` | closed_at lifecycle rule |
| 53-61 | `create_finding` | Cross-model VKB creation |
| 71-74 | `finding_detail` | Authorization branching |
| 80-83 | `edit_finding` | Authorization branching |
| 90-93 | `edit_finding` | closed_at lifecycle (duplicate) |
| 105-108 | `delete_finding` | Authorization branching |

### projects/views.py
| Line(s) | Function | Violation |
|---|---|---|
| 11-14 | `project_list` | Authorization branching |
| 25-28 | `project_create` | completed_date lifecycle |
| 42-45 | `project_update` | Authorization branching |
| 52-55 | `project_update` | completed_date lifecycle (duplicate) |
| 65-68 | `project_delete` | Authorization branching |
| 75-94 | `organization_detail` | Duplicate view + authorization |
| 103-106 | `project_detail` | Authorization branching |

### organizations/views.py
| Line(s) | Function | Violation |
|---|---|---|
| 10-14 | `organization_list` | Authorization branching |
| 52-63 | `organization_detail` | Authorization branching |

### reports/views.py
| Line(s) | Function | Violation |
|---|---|---|
| 19-28 | `generate_report` | History creation + thread spawning |
| 31-42 | `run` | Entire function is business logic |
| 51-54 | `download_report` | Format→MIME mapping |
| 58-61 | `download_report` | Preview vs download disposition |
| 70-77 | `delete_report` | File I/O + DB deletion |

### findings/models.py
| Line(s) | Method | Violation |
|---|---|---|
| 39-45 | `sla_days()` | Hardcoded SLA rules |
| 47-48 | `sla_due_date()` | Date arithmetic |
| 50-55 | `is_late()` | SLA breach evaluation |
| 57-64 | `sla_delay_days()` | Overdue calculation |

### projects/models.py
| Line(s) | Method | Violation |
|---|---|---|
| 24-42 | `spi()` | SPI KPI formula |

### reports/utils.py
| Line(s) | Function | Violation |
|---|---|---|
| 33-94 | `generate_report_file()` | Monolithic report assembly (60 lines, mixed rendering + I/O + dispatch) |

### vkb/views.py
| Line(s) | Function | Violation |
|---|---|---|
| 40-46 | `get_vkb_json` | Manual field serialization |

### roles/views.py
| Line(s) | Function | Violation |
|---|---|---|
| 15 | `role_create` | Post-save M2M sync |
| 27 | `role_update` | Post-save M2M sync (duplicate) |
| 51-53 | `role_detail` | Add menu to role |
| 58 | `role_detail` | Unassigned menus derivation |
| 64 | `remove_menu_from_role` | Remove menu from role |
