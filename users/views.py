from django.shortcuts import render, get_object_or_404, redirect
from .models import User
from .forms import UserForm
from django.contrib.auth.hashers import make_password

def user_list(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password_hash = make_password(form.cleaned_data['password_hash'])
            user.save()
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'users/user_form.html', {'form': form})

def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data['password_hash']
            if new_password:
                user.password_hash = make_password(new_password)
            user.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
        form.fields['password_hash'].initial = ''  # kosongkan field password saat edit
    return render(request, 'users/user_form.html', {'form': form})

def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'users/user_confirm_delete.html', {'user': user})
