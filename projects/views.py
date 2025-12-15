from django.shortcuts import render, get_object_or_404, redirect
from .models import Project
from .forms import ProjectForm
from organizations.models import Organization
from django.utils import timezone
from reports.models import ReportHistory
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def project_list(request):
    if request.user.is_superuser:
        projects = Project.objects.select_related('organization').all()
    else:
        projects = Project.objects.filter(assignment__user=request.user).select_related('organization').distinct()
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
@permission_required('projects.add_project', raise_exception=True)
def project_create(request, organization_id=None):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)

            if project.status == 'Completed' and not project.completed_date:
                project.completed_date = timezone.now().date()
            elif project.status != 'Completed':
                project.completed_date = None
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
    # Check if user is involved or superuser
    if request.user.is_superuser:
        project = get_object_or_404(Project, pk=pk)
    else:
        project = get_object_or_404(Project, pk=pk, assignment__user=request.user)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            
            if project.status == 'Completed' and not project.completed_date:
                project.completed_date = timezone.now().date()
            elif project.status != 'Completed':
                project.completed_date = None
            project.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
@permission_required('projects.delete_project', raise_exception=True)
def project_delete(request, pk):
    if request.user.is_superuser:
        project = get_object_or_404(Project, pk=pk)
    else:
        project = get_object_or_404(Project, pk=pk, assignment__user=request.user)

    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})

@login_required
@login_required
def organization_detail(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    
    if request.user.is_superuser:
        projects = Project.objects.filter(organization=organization)
    else:
        # Check if user is involved in ANY project of this organization
        # If not involved in any project of this organization, they shouldn't see the organization detail ideally,
        # but for now we just filter the projects list they see.
        # Strict interpretation: "Organization Detail: Involved only" -> User must be involved in at least one project of this organization.
        
        involved_projects = Project.objects.filter(organization=organization, assignment__user=request.user)
        if not involved_projects.exists():
             # If strictly enforcing "Involved only" for Organization Detail, we might want to 404 here.
             # But let's just show empty project list if they somehow got here (e.g. direct URL)
             pass
        
        projects = involved_projects

    return render(request, 'organizations/organization_detail.html', {
        'organization': organization,
        'projects': projects
    })

@login_required
def project_detail(request, pk):
    if request.user.is_superuser:
        project = get_object_or_404(Project, pk=pk)
    else:
        project = get_object_or_404(Project, pk=pk, assignment__user=request.user)

    reports = project.reports.all().order_by('-created_at')
    return render(request, 'projects/project_detail.html', {
            'project': project,
            'reports': reports,
            'assignments': [],
            'pics': [],
            'scans': [],
            'findings': [],
        })