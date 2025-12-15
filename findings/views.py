from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Finding
from .forms import FindingForm
from projects.models import Project
from vkb.models import VulnerabilityKnowledgeBase
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('findings.view_finding', raise_exception=True)
def finding_list(request):
    if request.user.is_superuser:
        findings_list = Finding.objects.select_related('project', 'project__organization').all().order_by('-created_at')
    else:
        findings_list = Finding.objects.filter(project__assignment__user=request.user).select_related('project', 'project__organization').distinct().order_by('-created_at')

    paginator = Paginator(findings_list, 10) # Show 10 findings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'findings/finding_list.html', {
        'page_obj': page_obj,
        'num_pages': paginator.num_pages
    })

@login_required
@permission_required('findings.add_finding', raise_exception=True)
def create_finding(request, project_id):
    if request.user.is_superuser:
        project = get_object_or_404(Project, pk=project_id)
    else:
        project = get_object_or_404(Project, pk=project_id, assignment__user=request.user)

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

    return render(request, 'findings/finding_form.html', {'form': form, 'project': project})

@login_required
def finding_detail(request, pk):
    if request.user.is_superuser:
        finding = get_object_or_404(Finding, pk=pk)
    else:
        finding = get_object_or_404(Finding, pk=pk, project__assignment__user=request.user)
    return render(request, 'findings/finding_detail.html', {'finding': finding})

@login_required
@permission_required('findings.change_finding', raise_exception=True)
def edit_finding(request, pk):
    if request.user.is_superuser:
        finding = get_object_or_404(Finding, pk=pk)
    else:
        finding = get_object_or_404(Finding, pk=pk, project__assignment__user=request.user)

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

@login_required
@permission_required('findings.delete_finding', raise_exception=True)
def delete_finding(request, pk):
    if request.user.is_superuser:
        finding = get_object_or_404(Finding, pk=pk)
    else:
        finding = get_object_or_404(Finding, pk=pk, project__assignment__user=request.user)

    project_id = finding.project.id
    if request.method == 'POST':
        finding.delete()
        return redirect('project_detail', pk=project_id)
    return render(request, 'findings/finding_confirm_delete.html', {'finding': finding})
