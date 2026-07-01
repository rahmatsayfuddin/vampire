from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from .models import Project
from .forms import ProjectForm
from .services import ProjectService
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
    return render(request, 'projects/project_detail.html', {
            'project': project,
            'reports': reports,
            'scans': [],
            'audit_logs': audit_logs,
        })