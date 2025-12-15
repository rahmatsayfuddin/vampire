"""
URL configuration for vampire project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from projects.models import Project
from findings.models import Finding

@login_required
def dashboard(request):
    # Basic stats for the dashboard
    if request.user.is_superuser:
        project_count = Project.objects.count()
        finding_count = Finding.objects.count()
    else:
        project_count = Project.objects.filter(assignment__user=request.user).count()
        finding_count = Finding.objects.filter(project__assignment__user=request.user).count()
    
    return render(request, 'dashboard.html', {
        'project_count': project_count,
        'finding_count': finding_count
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', dashboard, name='dashboard'), # Root URL now points to dashboard (which requires login)
    path('', include('users.urls')), # User/Role management
    path('organizations/', include('organizations.urls')),
    path('projects/', include('projects.urls')),
    path('assignments/', include('assignments.urls')),
    path('stakeholders/', include('stakeholders.urls')),
    path('vkb/', include('vkb.urls')),
    path('findings/', include('findings.urls')),
    path('reports/', include('reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
