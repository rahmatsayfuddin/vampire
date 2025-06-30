from django.shortcuts import render, get_object_or_404, redirect
from .models import Stakeholder
from .forms import StakeholderForm
from projects.models import Project

def add_stakeholder(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = StakeholderForm(request.POST)
        if form.is_valid():
            stakeholder = form.save(commit=False)
            stakeholder.project = project
            stakeholder.save()
            return redirect('project_detail', pk=project_id)
    else:
        form = StakeholderForm()
    return render(request, 'stakeholders/stakeholder_form.html', {'form': form, 'project': project})

def remove_stakeholder(request, stakeholder_id):
    stakeholder = get_object_or_404(Stakeholder, pk=stakeholder_id)
    project_id = stakeholder.project.pk
    if request.method == 'POST':
        stakeholder.delete()
        return redirect('project_detail', pk=project_id)
    return render(request, 'stakeholders/stakeholder_confirm_delete.html', {'stakeholder': stakeholder})
