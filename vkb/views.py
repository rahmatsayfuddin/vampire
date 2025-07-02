from django.shortcuts import render, get_object_or_404, redirect
from .models import VulnerabilityKnowledgeBase
from .forms import VKBForm

def vkb_list(request):
    items = VulnerabilityKnowledgeBase.objects.all()
    return render(request, 'vkb/vkb_list.html', {'items': items})

def vkb_create(request):
    if request.method == 'POST':
        form = VKBForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vkb_list')
    else:
        form = VKBForm()
    return render(request, 'vkb/vkb_form.html', {'form': form})

def vkb_update(request, pk):
    item = get_object_or_404(VulnerabilityKnowledgeBase, pk=pk)
    if request.method == 'POST':
        form = VKBForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('vkb_list')
    else:
        form = VKBForm(instance=item)
    return render(request, 'vkb/vkb_form.html', {'form': form})

def vkb_delete(request, pk):
    item = get_object_or_404(VulnerabilityKnowledgeBase, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('vkb_list')
    return render(request, 'vkb/vkb_confirm_delete.html', {'item': item})
