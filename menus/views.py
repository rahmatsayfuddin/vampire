from django.shortcuts import render, redirect, get_object_or_404
from .models import Menu
from .forms import MenuForm

def menu_list(request):
    menus = Menu.objects.all()
    return render(request, 'menus/menu_list.html', {'menus': menus})

def menu_create(request):
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('menu_list')
    else:
        form = MenuForm()
    return render(request, 'menus/menu_form.html', {'form': form})

def menu_update(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('menu_list')
    else:
        form = MenuForm(instance=menu)
    return render(request, 'menus/menu_form.html', {'form': form})

def menu_delete(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        menu.delete()
        return redirect('menu_list')
    return render(request, 'menus/menu_confirm_delete.html', {'menu': menu})
