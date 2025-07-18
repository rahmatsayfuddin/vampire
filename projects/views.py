from django.shortcuts import render, get_object_or_404, redirect
from .models import Project
from .forms import ProjectForm
from products.models import Product
from django.utils import timezone

def project_list(request):
    projects = Project.objects.select_related('product').all()
    return render(request, 'projects/project_list.html', {'projects': projects})

def project_create(request, product_id=None):
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
        if product_id:
            form.fields['product'].initial = product_id
            form.fields['product'].disabled = True 
    return render(request, 'projects/project_form.html', {'form': form})

def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form})

def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project': project})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    projects = Project.objects.filter(product=product)
    return render(request, 'projects/product_detail.html', {
        'product': product,
        'projects': projects
    })

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'projects/project_detail.html', {
        'project': project,
        # Placeholder untuk modul lainnya
        'assignments': [],  # nanti diisi
        'pics': [],
        'scans': [],
        'findings': [],
    })