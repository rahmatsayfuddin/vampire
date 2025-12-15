from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserForm, GroupForm

def is_manager_or_superuser(user):
    return user.is_superuser or user.groups.filter(name='Manager').exists()

@login_required
@user_passes_test(is_manager_or_superuser)
def user_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'users/user_list.html', {'users': users})

@login_required
@user_passes_test(is_manager_or_superuser)
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Create User'})

@login_required
@user_passes_test(is_manager_or_superuser)
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Edit User'})

@login_required
@user_passes_test(is_manager_or_superuser)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'users/user_confirm_delete.html', {'user': user})

# Group Views

@login_required
@user_passes_test(is_manager_or_superuser)
def group_list(request):
    groups = Group.objects.all().order_by('name')
    return render(request, 'users/group_list.html', {'groups': groups})

@login_required
@user_passes_test(is_manager_or_superuser)
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'users/group_form.html', {'form': form, 'title': 'Create Role'})

@login_required
@user_passes_test(is_manager_or_superuser)
def group_update(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_list')
    else:
        form = GroupForm(instance=group)
    return render(request, 'users/group_form.html', {'form': form, 'title': 'Edit Role'})

@login_required
@user_passes_test(is_manager_or_superuser)
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list')
    return render(request, 'users/group_confirm_delete.html', {'group': group})
