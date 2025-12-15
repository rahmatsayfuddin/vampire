from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .models import Assignment
from .forms import AssignmentForm
from projects.models import Project

@login_required
@permission_required('projects.change_project', raise_exception=True)
def add_assignment(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, project=project)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.project = project
            assignment.save()
            return redirect('project_detail', pk=project_id)
    else:
        form = AssignmentForm(project=project)

    return render(request, 'assignments/assignment_form.html', {
        'form': form,
        'project': project,
    })

@login_required
@permission_required('projects.change_project', raise_exception=True)
def remove_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    project_id = assignment.project.pk
    if request.method == 'POST':
        assignment.delete()
        return redirect('project_detail', pk=project_id)
    return render(request, 'assignments/assignment_confirm_delete.html', {'assignment': assignment})
