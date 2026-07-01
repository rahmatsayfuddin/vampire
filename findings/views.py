from django.shortcuts import render, get_object_or_404, redirect
from .models import Finding
from .forms import FindingForm
from .services import FindingService
from projects.models import Project
from projects.services import ProjectService
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('findings.view_finding', raise_exception=True)
def finding_list(request):
    findings_list = FindingService.get_queryset_for_user(request.user).order_by('-created_at')

    paginator = Paginator(findings_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'findings/finding_list.html', {
        'page_obj': page_obj,
        'num_pages': paginator.num_pages
    })

@login_required
@permission_required('findings.add_finding', raise_exception=True)
def create_finding(request, project_id):
    project = ProjectService.get_project_for_user(project_id, request.user)

    if request.method == 'POST':
        form = FindingForm(request.POST)
        if form.is_valid():
            finding = form.save(commit=False)
            finding.project = project

            selected_vkb = request.POST.get('vkb')
            if selected_vkb:
                finding.vkb_reference_id = selected_vkb

            FindingService.set_closed_at_by_status(finding)
            finding.save()

            if form.cleaned_data.get('save_to_vkb'):
                category = form.cleaned_data.get('vkb_category')
                FindingService.promote_to_vkb(finding, category)

            return redirect('project_detail', pk=project_id)
    else:
        form = FindingForm()

    return render(request, 'findings/finding_form.html', {'form': form, 'project': project})

@login_required
def finding_detail(request, pk):
    finding = FindingService.get_finding_for_user(pk, request.user)
    return render(request, 'findings/finding_detail.html', {'finding': finding})

@login_required
@permission_required('findings.change_finding', raise_exception=True)
def edit_finding(request, pk):
    finding = FindingService.get_finding_for_user(pk, request.user)

    if request.method == 'POST':
        form = FindingForm(request.POST, instance=finding)
        if form.is_valid():
            finding = form.save(commit=False)
            FindingService.set_closed_at_by_status(finding)
            finding.save()
            return redirect('finding_detail', pk=finding.pk)
    else:
        form = FindingForm(instance=finding)

    return render(request, 'findings/finding_form.html', {'form': form, 'project': finding.project})

@login_required
@permission_required('findings.delete_finding', raise_exception=True)
def delete_finding(request, pk):
    finding = FindingService.get_finding_for_user(pk, request.user)
    project_id = finding.project.id
    if request.method == 'POST':
        finding.delete()
        return redirect('project_detail', pk=project_id)
    return render(request, 'findings/finding_confirm_delete.html', {'finding': finding})
