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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from projects.models import Project
from projects.services import ProjectMetricsService
from findings.models import Finding
from findings.services import SlaService

@login_required
def dashboard(request):
    if request.user.is_superuser:
        findings = Finding.objects.select_related('project', 'project__organization').all()
        projects = Project.objects.select_related('organization').all()
    else:
        findings = Finding.objects.filter(project__assignment__user=request.user).select_related('project', 'project__organization')
        projects = Project.objects.filter(assignment__user=request.user).select_related('organization')

    project_count = projects.count()
    finding_count = findings.count()

    severity_counts = dict(
        Finding.objects.filter(pk__in=findings.values('pk'))
        .values_list('severity')
        .annotate(count=Count('id'))
        .order_by('severity')
    )

    late_count = sum(1 for f in findings if SlaService.is_late(f))
    on_time_count = finding_count - late_count
    sla_compliance = round((on_time_count / finding_count * 100) if finding_count > 0 else 100)

    on_track = sum(1 for p in projects if ProjectMetricsService.spi(p) is not None and ProjectMetricsService.spi(p) >= 1)
    delayed = project_count - on_track

    recent_findings = findings.order_by('-created_at')[:5]
    recent_projects = projects.order_by('-created_at')[:5]

    return render(request, 'dashboard.html', {
        'project_count': project_count,
        'finding_count': finding_count,
        'late_count': late_count,
        'sla_compliance': sla_compliance,
        'severity_labels': list(severity_counts.keys()),
        'severity_data': list(severity_counts.values()),
        'severity_counts': severity_counts,
        'on_track': on_track,
        'delayed': delayed,
        'recent_findings': recent_findings,
        'recent_projects': recent_projects,
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
