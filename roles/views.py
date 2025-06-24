from django.shortcuts import get_object_or_404, redirect, render
from menus.models import Menu
from .models import Role, RoleMenuAccess
from .forms import RoleForm

def role_list(request):
    roles = Role.objects.all()
    return render(request, 'roles/role_list.html', {'roles': roles})

def role_create(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            role.menus.set(form.cleaned_data['menus'])
            return redirect('role_list')
    else:
        form = RoleForm()
    return render(request, 'roles/role_form.html', {'form': form})

def role_update(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save()
            role.menus.set(form.cleaned_data['menus'])
            return redirect('role_list')
    else:
        form = RoleForm(instance=role)
        form.fields['menus'].initial = role.menus.all()
    return render(request, 'roles/role_form.html', {'form': form})

def role_delete(request, pk):
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        role.delete()
        return redirect('role_list')
    return render(request, 'roles/role_confirm_delete.html', {'role': role})


def role_detail(request, pk):
    role = get_object_or_404(Role, pk=pk)
    all_menus = Menu.objects.all()
    assigned_menus = role.menus.all()

    if request.method == 'POST':
        # Assign new menu
        selected_menu_id = request.POST.get('menu_id')
        if selected_menu_id:
            menu = get_object_or_404(Menu, pk=selected_menu_id)
            role.menus.add(menu)
            return redirect('role_detail', pk=role.pk)

    return render(request, 'roles/role_detail.html', {
        'role': role,
        'assigned_menus': assigned_menus,
        'unassigned_menus': all_menus.exclude(pk__in=assigned_menus),
    })

def remove_menu_from_role(request, role_id, menu_id):
    role = get_object_or_404(Role, pk=role_id)
    menu = get_object_or_404(Menu, pk=menu_id)
    role.menus.remove(menu)
    return redirect('role_detail', pk=role.pk)
