import os
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_POST

from .models import ReportHistory
from projects.models import Project
from .services import ReportService, ReportGenerationService


@require_POST
def generate_report(request, project_id, format):
    project = get_object_or_404(Project, id=project_id)

    history = ReportGenerationService.create_history(project, format)
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
