# Usage Guide

## 1. Create an Admin User

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password. This account has full access to all features including Administration menus.

## 2. Create an Organization

Navigate to **Organizations** → **Add New Organization**.

| Field | Description |
|---|---|
| Name | Organization/company name (required) |
| Logo | Upload an image file (optional, PNG/JPG) |
| Description | Brief description (optional) |

Click **Save**. The organization appears in the list and is available when creating projects.

## 3. Configure SLA Profiles (Admin)

Navigate to **Administration** → **SLA Profiles** → **Add SLA Profile**.

| Field | Description |
|---|---|
| Name | Profile name, e.g. "Critical Infrastructure" |
| SLA Critical | Days allowed for Critical findings (default: 7) |
| SLA High | Days allowed for High findings (default: 14) |
| SLA Medium | Days allowed for Medium findings (default: 30) |
| SLA Low | Days allowed for Low findings (default: 60) |
| Is Default | Auto-applied to projects without a profile |

Check **Is Default** to set this as the fallback SLA. Only one profile can be the default at a time — checking it automatically clears the previous default.

## 4. Create a Project

Navigate to **Projects** → **Create New Project**.

| Field | Description |
|---|---|
| Project Name | Unique project identifier |
| Organization | Select from dropdown (TomSelect searchable) |
| SLA Profile | Choose a profile or leave empty for default SLA |
| Start Date | Click to open flatpickr date picker |
| End Date | Project deadline |
| Status | Planned / In Progress / Completed / On Hold |
| Description | Project overview |
| Scope | Assessment boundary |

Click **Save**. The project appears in the list with its SPI indicator.

> **Tip:** Set status to **Completed** and the system auto-fills the completed date. Change back to another status to clear it.

## 5. Assign Team Members

Open a **Project Detail** page → click **Assign User**.

| Field | Description |
|---|---|
| User | Select from TomSelect dropdown (search by name) |
| Title | Role, e.g. "Lead Pentester" |

Click **Assign**. The team member appears in the Assignments list. Click **Remove** to unassign.

## 6. Add Stakeholders

Open a **Project Detail** page → click **Add Stakeholder**.

| Field | Description |
|---|---|
| Name | Stakeholder name |
| Email | Contact email |
| Position | Role, e.g. "CTO" |

Click **Add**. Stakeholders are included in generated reports.

## 7. Upload & Parse Scan Reports

Open a **Project Detail** page → **Scanning Reports** card → **Upload Scan**.

| Field | Description |
|---|---|
| Source Tool | Burp, ZAP, Nessus, Acunetix, Nmap, OpenVAS, or Generic CSV |
| File | Scan export file |

Click **Upload**. The file appears in the scan table with status **Pending**. Click **Parse** to extract findings asynchronously. Status changes to **Parsing...** then **Done**.

Use the **Trend** tab to see severity counts per scan, and the **Compare** tab to compare two scans side-by-side (New / Recurring / Solved).

On the **Scan Detail** page, click **Add** to promote a finding to a tracked Finding, or **FP** to mark it as a false positive.

## 8. Create a Finding (3-Step Wizard)

Open a **Project Detail** page → click **Add Finding**. The wizard guides you through three steps:

**Step 1 — Choose Template:**
- Select a VKB entry from the dropdown to auto-fill the form (see §9), or
- Click **Start from Scratch** to enter data manually.

**Step 2 — Fill Details:**

| Field | Description |
|---|---|
| Title | Finding title |
| Severity | Critical / High / Medium / Low |
| Status | Open / Closed / Risk Acceptance |
| CVSS Score | Numeric score (optional) |
| Affected Asset | Affected system or URL |
| Description | Detailed description |
| Impact | Business/technical impact |
| Recommendation | Remediation guidance |
| **Proof of Concept** | Quill.js rich-text editor |

Use the **Quill toolbar** for formatting: bold, italic, lists, code blocks, blockquotes, links, and image upload. Click the **image button** → select a file → the image uploads to the server and is inserted at the cursor position.

Click **Save Finding**.

**Step 3 — Save to VKB (optional):**
- Check **Save to VKB** to reuse this finding as a template, select a category.
- Click **Save to VKB & Finish**, or **Skip & Go to Project**.

## 9. Use VKB Templates

Navigate to **VKB** → **Create**.

| Field | Description |
|---|---|
| Category | One of 8 standard categories |
| Title | Template title |
| Description | Vulnerability description |
| Impact | Expected impact |
| Recommendation | Remediation steps |

Click **Save**. In the finding wizard Step 1, select a VKB entry from the dropdown — the title, description, impact, and recommendation auto-fill into the form.

## 10. Edit the Report Template (Admin)

Navigate to **Administration** → **Report Template**. This page shows the current Markdown template with available Django template variables:

| Variable | Description |
|---|---|
| `{{ project }}` | Current project object |
| `{{ findings }}` | List of findings |
| `{{ today }}` | Report generation date |

Use `{% for finding in findings %}` to iterate findings. Edit the content, click **Save**. All subsequent reports will use the updated template.

## 11. Generate & Preview Reports

Open a **Project Detail** page → click **Generate Report**. The system creates the report in the background (status: **Loading**). When complete, it changes to **Done**.

| Action | Description |
|---|---|
| **Preview** | Opens the Markdown rendered as styled HTML in a new tab |
| **Download** | Downloads the `.md` file |
| **Delete** | Removes the report file and history record |

> If generation fails, status shows **Failed**. Check server logs for error details.

Navigate to **Reports** in the sidebar for a global report list with **Project**, **Format**, and **Status** filter dropdowns.

## 12. Search & Filter Findings

Navigate to **Findings** in the sidebar. Use the filter toolbar:

| Filter | Type | Description |
|---|---|---|
| Search box | Text | Matches title or description (case-insensitive) |
| Severity | Dropdown | Critical / High / Medium / Low |
| Status | Dropdown | Open / Closed / Risk Acceptance |
| Project | Dropdown | All user-assigned projects |
| Date From / To | Date picker | Filter by creation date range |

Click **Filter** to apply, **Clear** to reset. Pagination automatically preserves your active filter parameters.
