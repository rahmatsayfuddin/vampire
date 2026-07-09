from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.conf import settings
from django.db.models import Count, Q
import threading, os, json, hashlib
from collections import defaultdict
from .models import Project, SlaProfile, ScanReport, ScanFinding, ProjectNote
from .forms import ProjectForm, SlaProfileForm
from .services import ProjectService, ProjectMetricsService
from .parsers import PARSERS
from findings.models import Finding
from findings.services import SlaService
from audit.models import AuditLog
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def project_list(request):
    projects = ProjectService.get_queryset_for_user(request.user)
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
@permission_required('projects.add_project', raise_exception=True)
def project_create(request, organization_id=None):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            ProjectService.set_completed_date_by_status(project)
            project._audit_user = request.user
            project.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
        if organization_id:
            form.fields['organization'].initial = organization_id
            form.fields['organization'].disabled = True
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
@permission_required('projects.change_project', raise_exception=True)
def project_update(request, pk):
    project = ProjectService.get_project_for_user(pk, request.user)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            ProjectService.set_completed_date_by_status(project)
            project._audit_user = request.user
            project.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
@permission_required('projects.delete_project', raise_exception=True)
def project_delete(request, pk):
    project = ProjectService.get_project_for_user(pk, request.user)

    if request.method == 'POST':
        project._audit_user = request.user
        project.delete()
        return redirect('project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})


def _scan_comparison(scan_reports):
    by_tool = defaultdict(list)
    for sr in scan_reports:
        if sr.status == 'done':
            by_tool[sr.source_tool].append(sr)

    flags = {}
    solved = defaultdict(list)

    for tool, reports in by_tool.items():
        reports.sort(key=lambda r: r.uploaded_at)
        prev_hashes = set()
        prev_findings = []

        for sr in reports:
            current = {}
            for sf in sr.findings.all():
                h = hashlib.md5((sf.title + sf.affected.lower()).encode()).hexdigest()
                current[h] = sf

            current_hashes = set(current.keys())

            if prev_hashes:
                new_hashes = current_hashes - prev_hashes
                recurring_hashes = current_hashes & prev_hashes

                for h, sf in current.items():
                    if h in new_hashes:
                        flags[sf.pk] = 'new'
                    elif h in recurring_hashes:
                        flags[sf.pk] = 'recurring'

                for pf in prev_findings:
                    h = hashlib.md5((pf['title'] + pf['affected'].lower()).encode()).hexdigest()
                    if h not in current_hashes:
                        solved[sr.pk].append(pf)

            prev_hashes = current_hashes
            prev_findings = [
                {'title': sf.title, 'severity': sf.severity, 'affected': sf.affected}
                for sf in current.values()
            ]

    return flags, dict(solved)


@login_required
def project_detail(request, pk):
    project = ProjectService.get_project_for_user(pk, request.user)

    if request.method == 'POST' and request.POST.get('note_content', '').strip():
        ProjectNote.objects.create(
            project=project, user=request.user,
            content=request.POST['note_content'].strip()
        )
        return redirect('project_detail', pk=project.pk)

    reports = project.reports.all().order_by('-created_at')
    content_type = ContentType.objects.get_for_model(Project)
    audit_logs = AuditLog.objects.filter(content_type=content_type, object_id=project.pk)[:10]
    scan_reports = project.scan_reports.all().order_by('-uploaded_at')
    notes = project.notes.all()[:20]

    project_findings = Finding.objects.filter(project=project)
    finding_count = project_findings.count()
    severity_counts = dict(project_findings.values_list('severity').annotate(count=Count('id')))
    late_count = sum(1 for f in project_findings if SlaService.is_late(f))
    sla_compliance = round(((finding_count - late_count) / finding_count * 100) if finding_count > 0 else 100)
    spi = ProjectMetricsService.spi(project)
    spi_status = 'on_track' if spi is not None and spi >= 1 else 'delayed' if spi is not None else 'unknown'

    tools = set(scan_reports.values_list('source_tool', flat=True))
    trend_data = {}
    scans_by_tool = {}
    for tool in tools:
        scans = list(scan_reports.filter(source_tool=tool).order_by('-uploaded_at'))
        scans_by_tool[tool] = scans
        trend_scans = list(reversed(scans[:5]))
        sev_order = ['Critical', 'High', 'Medium', 'Low']
        if trend_scans:
            trend_data[tool] = {
                'scans': [{'id': s.pk, 'date': s.uploaded_at.strftime('%m/%d')} for s in trend_scans],
                'datasets': [
                    {'label': sev, 'data': dict(
                        (s.pk, s.findings.filter(severity=sev).count()) for s in trend_scans
                    ), 'backgroundColor': {'Critical': '#212529', 'High': '#dc3545', 'Medium': '#ffc107', 'Low': '#0d6efd'}[sev]}
                    for sev in sev_order
                ]
            }

    scan_list_data = []
    for sr in scan_reports:
        scan_list_data.append({
            'id': sr.pk,
            'tool': sr.source_tool,
            'tool_display': sr.get_source_tool_display(),
            'file': os.path.basename(sr.file.name),
            'date': sr.uploaded_at.strftime('%m/%d'),
            'status': sr.status,
            'findings': sr.findings.count(),
        })

    return render(request, 'projects/project_detail.html', {
            'project': project,
            'reports': reports,
            'scan_reports': scan_reports,
            'notes': notes,
            'finding_count': finding_count,
            'severity_counts': severity_counts,
            'severity_labels': list(severity_counts.keys()),
            'severity_data': list(severity_counts.values()),
            'sla_compliance': sla_compliance,
            'late_count': late_count,
            'spi': spi,
            'spi_status': spi_status,
            'trend_data': json.dumps(trend_data),
            'scan_list_data': json.dumps(scan_list_data),
            'audit_logs': audit_logs,
        })


def _run_parse(report_id):
    from .models import ScanReport, ScanFinding
    report = ScanReport.objects.get(pk=report_id)
    try:
        parser = PARSERS[report.source_tool]
        parsed = parser(report.file.path)
        for item in parsed:
            ScanFinding.objects.create(report=report, **item)
        report.status = 'done'
    except Exception as e:
        report.status = 'error'
        print(f'Scan parse error: {e}')
    report.save()


@login_required
@permission_required('projects.change_project', raise_exception=True)
def upload_scan(request, pk):
    project = ProjectService.get_project_for_user(pk, request.user)
    if request.method == 'POST' and request.FILES.get('file'):
        ScanReport.objects.create(
            project=project,
            file=request.FILES['file'],
            source_tool=request.POST.get('source_tool', 'csv'),
            uploaded_by=request.user,
        )
    return redirect('project_detail', pk=project.id)


@login_required
@permission_required('projects.change_project', raise_exception=True)
def parse_scan(request, pk, report_id):
    report = get_object_or_404(ScanReport, pk=report_id, project__id=pk)
    if report.status != 'pending':
        return redirect('project_detail', pk=pk)
    report.status = 'parsing'
    report.save()
    threading.Thread(target=_run_parse, args=(report.pk,)).start()
    return redirect('project_detail', pk=pk)


@login_required
def download_scan(request, report_id):
    report = get_object_or_404(ScanReport, id=report_id)
    path = report.file.path
    if os.path.exists(path):
        with open(path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(report.file.name)}"'
            return response
    return HttpResponseNotFound('File not found.')


@login_required
@permission_required('findings.add_finding', raise_exception=True)
def promote_scan_finding(request, pk, sf_id):
    project = ProjectService.get_project_for_user(pk, request.user)
    sf = get_object_or_404(ScanFinding, pk=sf_id, report__project=project)
    if sf.promoted_to:
        return redirect('scan_detail', report_id=sf.report.pk)
    from findings.models import Finding
    finding = Finding.objects.create(
        project=project,
        title=sf.title,
        description=sf.description,
        impact=f'[From {sf.report.source_tool}] {sf.severity}',
        recommendation=sf.recommendation,
        severity=sf.severity,
        affected=sf.affected or 'Not specified',
        status='Open',
    )
    sf.promoted_to = finding
    sf.save()
    return redirect('scan_detail', report_id=sf.report.pk)


@login_required
@permission_required('projects.change_project', raise_exception=True)
def tag_scan_fp(request, pk, sf_id):
    sf = get_object_or_404(ScanFinding, pk=sf_id, report__project__id=pk)
    sf.is_false_positive = True
    sf.save()
    return redirect('scan_detail', report_id=sf.report.pk)


@login_required
def scan_detail(request, report_id):
    report = get_object_or_404(ScanReport.objects.select_related('project__organization'), pk=report_id)
    ProjectService.get_project_for_user(report.project.pk, request.user)

    all_scans = list(ScanReport.objects.filter(
        project=report.project, source_tool=report.source_tool
    ).order_by('-uploaded_at'))
    comparison_flags, solved_map = _scan_comparison(all_scans)

    findings = list(report.findings.all().order_by('severity', 'title'))
    for sf in findings:
        sf.comparison_flag = comparison_flags.get(sf.pk)

    return render(request, 'projects/scan_detail.html', {
        'report': report,
        'findings': findings,
        'solved_findings': solved_map.get(report.pk, []),
        'project': report.project,
    })


@login_required
@permission_required('projects.change_project', raise_exception=True)
def delete_scan(request, report_id):
    report = get_object_or_404(ScanReport, pk=report_id)
    project_pk = report.project.pk
    ProjectService.get_project_for_user(project_pk, request.user)
    report.delete()
    return redirect('project_detail', pk=project_pk)


@login_required
def compare_scans(request, pk):
    project = ProjectService.get_project_for_user(pk, request.user)
    a_id = request.GET.get('a', '')
    b_id = request.GET.get('b', '')
    if not a_id or not b_id:
        return HttpResponseNotFound('Missing scan IDs')

    report_a = get_object_or_404(ScanReport, pk=a_id, project=project)
    report_b = get_object_or_404(ScanReport, pk=b_id, project=project)

    if report_a.source_tool != report_b.source_tool:
        return HttpResponseNotFound('Scans must be from the same tool')

    new_items, recurring_items, solved_items = _compare_pair(report_a, report_b)
    return JsonResponse({
        'new': new_items,
        'recurring': recurring_items,
        'solved': solved_items,
    })


def _compare_pair(report_a, report_b):
    a_map = {}
    for sf in report_a.findings.all():
        h = hashlib.md5((sf.title + sf.affected.lower()).encode()).hexdigest()
        a_map[h] = {'title': sf.title, 'severity': sf.severity, 'affected': sf.affected}

    b_map = {}
    for sf in report_b.findings.all():
        h = hashlib.md5((sf.title + sf.affected.lower()).encode()).hexdigest()
        b_map[h] = {'pk': sf.pk, 'title': sf.title, 'severity': sf.severity,
                    'affected': sf.affected, 'is_fp': sf.is_false_positive,
                    'promoted': sf.promoted_to_id}

    a_set, b_set = set(a_map), set(b_map)
    return (
        [b_map[h] for h in (b_set - a_set)],
        [b_map[h] for h in (a_set & b_set)],
        [a_map[h] for h in (a_set - b_set)],
    )


@login_required
@permission_required('projects.add_project', raise_exception=True)
def sla_profile_list(request):
    profiles = SlaProfile.objects.all()
    return render(request, 'projects/sla_profile_list.html', {'profiles': profiles})


@login_required
@permission_required('projects.add_project', raise_exception=True)
def sla_profile_create(request):
    if request.method == 'POST':
        form = SlaProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sla_profile_list')
    else:
        form = SlaProfileForm()
    return render(request, 'projects/sla_profile_form.html', {'form': form, 'title': 'Create SLA Profile'})


@login_required
@permission_required('projects.change_project', raise_exception=True)
def sla_profile_update(request, pk):
    profile = get_object_or_404(SlaProfile, pk=pk)
    if request.method == 'POST':
        form = SlaProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('sla_profile_list')
    else:
        form = SlaProfileForm(instance=profile)
    return render(request, 'projects/sla_profile_form.html', {'form': form, 'title': 'Edit SLA Profile'})


@login_required
@permission_required('projects.delete_project', raise_exception=True)
def sla_profile_delete(request, pk):
    profile = get_object_or_404(SlaProfile, pk=pk)
    if request.method == 'POST':
        profile.delete()
        return redirect('sla_profile_list')
    return render(request, 'projects/sla_profile_confirm_delete.html', {'profile': profile})