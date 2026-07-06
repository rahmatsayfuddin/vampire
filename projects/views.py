from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
import threading, os
from .models import Project, SlaProfile, ScanReport, ScanFinding
from .forms import ProjectForm, SlaProfileForm
from .services import ProjectService
from .parsers import PARSERS
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

@login_required
def project_detail(request, pk):
    project = ProjectService.get_project_for_user(pk, request.user)

    reports = project.reports.all().order_by('-created_at')
    content_type = ContentType.objects.get_for_model(Project)
    audit_logs = AuditLog.objects.filter(content_type=content_type, object_id=project.pk)[:10]
    scan_reports = project.scan_reports.all().order_by('-uploaded_at')
    return render(request, 'projects/project_detail.html', {
            'project': project,
            'reports': reports,
            'scan_reports': scan_reports,
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
def upload_scan(request, project_id):
    project = ProjectService.get_project_for_user(project_id, request.user)
    if request.method == 'POST' and request.FILES.get('file'):
        report = ScanReport.objects.create(
            project=project,
            file=request.FILES['file'],
            source_tool=request.POST.get('source_tool', 'csv'),
            uploaded_by=request.user,
        )
        threading.Thread(target=_run_parse, args=(report.id,)).start()
    return redirect('project_detail', pk=project.id)


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
def promote_scan_finding(request, project_id, sf_id):
    project = ProjectService.get_project_for_user(project_id, request.user)
    sf = get_object_or_404(ScanFinding, pk=sf_id, report__project=project)
    if sf.promoted_to:
        return redirect('project_detail', pk=project_id)
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
    return redirect('project_detail', pk=project_id)


@login_required
@permission_required('projects.change_project', raise_exception=True)
def tag_scan_fp(request, project_id, sf_id):
    sf = get_object_or_404(ScanFinding, pk=sf_id, report__project__id=project_id)
    sf.is_false_positive = True
    sf.save()
    return redirect('project_detail', pk=project_id)


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