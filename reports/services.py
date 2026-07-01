import os
import threading
from django.conf import settings
from findings.models import Finding
from .models import ReportHistory


MIME_MAP = {
    'md': 'text/markdown',
}


class ReportService:

    @staticmethod
    def get_mime_type(format):
        return MIME_MAP.get(format, 'application/octet-stream')

    @staticmethod
    def get_disposition(report, preview=False):
        return f'attachment; filename="{report.file_name}"'

    @staticmethod
    def delete_report_file(report):
        path = os.path.join(settings.MEDIA_ROOT, 'reports', report.file_name)
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def file_exists(report):
        path = os.path.join(settings.MEDIA_ROOT, 'reports', report.file_name)
        return os.path.exists(path)


class ReportGenerationService:

    @staticmethod
    def create_history(project, format):
        return ReportHistory.objects.create(
            project=project,
            format=format,
            status='loading',
        )

    @staticmethod
    def generate_async(history_id):
        from .utils import generate_report_file

        try:
            history = ReportHistory.objects.get(id=history_id)
            project = history.project
            findings = Finding.objects.filter(project=project)

            filename = generate_report_file(project, findings, format=history.format)

            history.file_name = filename
            history.status = 'done'
            history.save()
        except Exception:
            history = ReportHistory.objects.get(id=history_id)
            history.status = 'failed'
            history.save()
            raise

    @staticmethod
    def start_generation(history_id):
        thread = threading.Thread(
            target=ReportGenerationService.generate_async,
            args=(history_id,),
        )
        thread.start()
