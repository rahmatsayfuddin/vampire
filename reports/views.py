import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import ReportHistory
from projects.models import Project
from .services import ReportService, ReportGenerationService


@login_required
def report_list(request):
    if request.user.is_superuser:
        reports = ReportHistory.objects.select_related('project__organization').all()
        projects = Project.objects.all()
    else:
        reports = ReportHistory.objects.filter(project__assignment__user=request.user).select_related('project__organization')
        projects = Project.objects.filter(assignment__user=request.user)

    project_id = request.GET.get('project', '')
    if project_id:
        reports = reports.filter(project_id=project_id)

    fmt = request.GET.get('format', '')
    if fmt:
        reports = reports.filter(format=fmt)

    st = request.GET.get('status', '')
    if st:
        reports = reports.filter(status=st)

    reports = reports.order_by('-created_at')

    paginator = Paginator(reports, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    query_string = query_params.urlencode()

    return render(request, 'reports/report_list.html', {
        'page_obj': page_obj,
        'num_pages': paginator.num_pages,
        'projects': projects,
        'query_string': query_string,
        'filters': {
            'project': project_id,
            'format': fmt,
            'status': st,
        }
    })


@require_POST
def generate_report(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    history = ReportGenerationService.create_history(project, 'md')
    ReportGenerationService.start_generation(history.id)

    return redirect('project_detail', pk=project.id)


def download_report(request, report_id):
    report = get_object_or_404(ReportHistory, id=report_id)
    path = os.path.join(settings.MEDIA_ROOT, 'reports', report.file_name)

    if not ReportService.file_exists(report):
        return HttpResponseNotFound('File not found.')

    with open(path, 'rb') as f:
        mime_type = ReportService.get_mime_type(report.format)
        response = HttpResponse(f.read(), content_type=mime_type)
        preview = request.GET.get('preview') == 'true'
        response['Content-Disposition'] = ReportService.get_disposition(report, preview)
        return response


@require_POST
def delete_report(request, report_id):
    report = get_object_or_404(ReportHistory, id=report_id)

    ReportService.delete_report_file(report)
    report.delete()

    return redirect('project_detail', pk=report.project.id)
