from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Finding
from .forms import FindingForm
from projects.models import Project
from vkb.models import VulnerabilityKnowledgeBase

def create_finding(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = FindingForm(request.POST)
        if form.is_valid():
            finding = form.save(commit=False)
            finding.project = project

            # Set VKB reference if selected
            selected_vkb = request.POST.get('vkb')
            if selected_vkb:
                finding.vkb_reference_id = selected_vkb

            # Set closed_at if status is "Closed"
            if finding.status == 'Closed' and not finding.closed_at:
                finding.closed_at = timezone.now()
            elif finding.status != 'Closed':
                finding.closed_at = None

            finding.save()

            # Save to VKB if checkbox checked and custom entry
    if form.cleaned_data.get('save_to_vkb'):
        category = form.cleaned_data.get('vkb_category') or 'Other Notable Vulnerabilities'
        VulnerabilityKnowledgeBase.objects.create(
            title=finding.title,
            description=finding.description,
            impact=finding.impact,
            recommendation=finding.recommendation,
            category=category
        )
        return redirect('project_detail', pk=project_id)
    else:
        form = FindingForm()

    return render(request, 'findings/finding_form.html', {
        'form': form,
        'project': project
    })

def finding_detail(request, pk):
    finding = get_object_or_404(Finding, pk=pk)
    return render(request, 'findings/finding_detail.html', {'finding': finding})
def create_finding(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = FindingForm(request.POST)
        if form.is_valid():
            finding = form.save(commit=False)
            finding.project = project

            selected_vkb = request.POST.get('vkb')
            if selected_vkb:
                finding.vkb_reference_id = selected_vkb

            if finding.status == 'Closed' and not finding.closed_at:
                finding.closed_at = timezone.now()
            elif finding.status != 'Closed':
                finding.closed_at = None

            finding.save()

            if form.cleaned_data.get('save_to_vkb'):
                VulnerabilityKnowledgeBase.objects.create(
                    title=finding.title,
                    description=finding.description,
                    impact=finding.impact,
                    recommendation=finding.recommendation,
                    category_id=1
                )

            return redirect('project_detail', pk=project_id)
    else:
        form = FindingForm()

    return render(request, 'findings/finding_form.html', {'form': form, 'project': project})

def finding_detail(request, pk):
    finding = get_object_or_404(Finding, pk=pk)
    return render(request, 'findings/finding_detail.html', {'finding': finding})

def edit_finding(request, pk):
    finding = get_object_or_404(Finding, pk=pk)
    if request.method == 'POST':
        form = FindingForm(request.POST, instance=finding)
        if form.is_valid():
            finding = form.save(commit=False)

            if finding.status == 'Closed' and not finding.closed_at:
                finding.closed_at = timezone.now()
            elif finding.status != 'Closed':
                finding.closed_at = None

            finding.save()
            return redirect('finding_detail', pk=finding.pk)
    else:
        form = FindingForm(instance=finding)

    return render(request, 'findings/finding_form.html', {'form': form, 'project': finding.project})

def delete_finding(request, pk):
    finding = get_object_or_404(Finding, pk=pk)
    project_id = finding.project.id
    if request.method == 'POST':
        finding.delete()
        return redirect('project_detail', pk=project_id)
    return render(request, 'findings/finding_confirm_delete.html', {'finding': finding})
