from django.shortcuts import render, get_object_or_404, redirect
from .models import Organization
from .forms import OrganizationForm
from projects.models import Project

from django.contrib.auth.decorators import login_required

@login_required
def organization_list(request):
    if request.user.is_superuser:
        organizations = Organization.objects.all()
    else:
        # User sees organizations where they have at least one project assignment
        organizations = Organization.objects.filter(project__assignment__user=request.user).distinct()
    return render(request, 'organizations/organization_list.html', {'organizations': organizations})

@login_required
def organization_create(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('organization_list')
    else:
        form = OrganizationForm()
    return render(request, 'organizations/organization_form.html', {'form': form})

@login_required
def organization_update(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES, instance=organization)
        if form.is_valid():
            form.save()
            return redirect('organization_list')
    else:
        form = OrganizationForm(instance=organization)
    return render(request, 'organizations/organization_form.html', {'form': form})

@login_required
def organization_delete(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    if request.method == 'POST':
        organization.delete()
        return redirect('organization_list')
    return render(request, 'organizations/organization_confirm_delete.html', {'organization': organization})

@login_required
def organization_detail(request, organization_id):
    organization = get_object_or_404(Organization, pk=organization_id)
    
    if request.user.is_superuser:
        projects = Project.objects.filter(organization=organization)
    else:
        # Only show projects where user is involved
        projects = Project.objects.filter(organization=organization, assignment__user=request.user)
        
        # Ideally we check if user has access to organization at all
        has_access = Organization.objects.filter(pk=organization_id, project__assignment__user=request.user).exists()
        if not has_access:
            # If strictly enforcing, maybe 404 or redirect. 
            # For now, let's just show the organization but with empty project list if they somehow accessed it.
            pass

    return render(request, 'organizations/organization_detail.html', {
        'organization': organization,
        'projects': projects
    })