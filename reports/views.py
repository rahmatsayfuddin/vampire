import os
import threading
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_POST

from .models import ReportHistory
from projects.models import Project
from findings.models import Finding
from .utils import generate_report_file


@require_POST
def generate_report(request, project_id, format):
    project = get_object_or_404(Project, id=project_id)

    # Buat record terlebih dahulu
    history = ReportHistory.objects.create(
        project=project,
        format=format,
        status='loading'
    )

    # Jalankan background task dengan ID
    threading.Thread(target=run, args=(history.id,)).start()

    return redirect('project_detail', pk=project.id)


def run(history_id):
    history = ReportHistory.objects.get(id=history_id)
    project = history.project
    findings = Finding.objects.filter(project=project)

    # Buat file report
    filename = generate_report_file(project, findings, format=history.format)

    # Update history setelah selesai
    history.file_name = filename
    history.status = 'done'
    history.save()


def download_report(request, report_id):
    report = get_object_or_404(ReportHistory, id=report_id)
    path = os.path.join(settings.MEDIA_ROOT, 'reports', report.file_name)

    if os.path.exists(path):
        with open(path, 'rb') as f:
            mime_type = (
                'application/pdf'
                if report.format == 'pdf'
                else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response = HttpResponse(f.read(), content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{report.file_name}"'
            return response
    else:
        return HttpResponseNotFound("File not found.")


@require_POST
def delete_report(request, report_id):
    report = get_object_or_404(ReportHistory, id=report_id)
    path = os.path.join(settings.MEDIA_ROOT, 'reports', report.file_name)

    # Hapus file jika ada
    if os.path.exists(path):
        os.remove(path)

    # Hapus record dari DB
    report.delete()

    return redirect('project_detail', pk=report.project.id)
