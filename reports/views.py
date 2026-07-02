import os
import markdown
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import ReportHistory, ReportTemplate
from .forms import ReportTemplateForm
from projects.models import Project
from .services import ReportService, ReportGenerationService


def _get_report_for_user(report_id, user):
    if user.is_superuser:
        return get_object_or_404(ReportHistory, id=report_id)
    return get_object_or_404(ReportHistory, id=report_id, project__assignment__user=user)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_template(request):
    template, _ = ReportTemplate.objects.get_or_create(
        pk=1,
        defaults={'content': open('reports/templates/reports/report_template.md').read()},
    )

    if request.method == 'POST':
        form = ReportTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            return redirect('edit_report_template')
    else:
        form = ReportTemplateForm(instance=template)

    return render(request, 'reports/edit_template.html', {'form': form})


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


@login_required
@require_POST
def generate_report(request, project_id):
    if request.user.is_superuser:
        project = get_object_or_404(Project, id=project_id)
    else:
        project = get_object_or_404(Project, id=project_id, assignment__user=request.user)

    history = ReportGenerationService.create_history(project, 'md')
    ReportGenerationService.start_generation(history.id)

    return redirect('project_detail', pk=project.id)


@login_required
def preview_report(request, report_id):
    report = _get_report_for_user(report_id, request.user)
    path = os.path.join(settings.MEDIA_ROOT, 'reports', report.file_name)

    if not ReportService.file_exists(report):
        return HttpResponseNotFound('File not found.')

    with open(path, 'r') as f:
        md_content = f.read()

    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'codehilite'])
    return HttpResponse(f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{report.file_name} — Preview</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
<style>
    body {{ padding: 2rem; max-width: 900px; margin: 0 auto; }}
    h1 {{ border-bottom: 2px solid #dee2e6; padding-bottom: 0.5rem; }}
    h2 {{ margin-top: 1.5rem; }}
    h3 {{ margin-top: 1.2rem; color: #495057; }}
    table {{ margin: 1rem 0; }}
    hr {{ margin: 2rem 0; }}
    code {{ background: #f8f9fa; padding: 2px 6px; border-radius: 3px; }}
    pre {{ background: #f8f9fa; padding: 1rem; border-radius: 5px; }}
    img {{ max-width: 100%; }}
    blockquote {{ border-left: 4px solid #dee2e6; padding-left: 1rem; color: #6c757d; }}
</style>
</head>
<body>{html_content}</body>
</html>''')


def download_report(request, report_id):
    report = _get_report_for_user(report_id, request.user)
    path = os.path.join(settings.MEDIA_ROOT, 'reports', report.file_name)

    if not ReportService.file_exists(report):
        return HttpResponseNotFound('File not found.')

    with open(path, 'rb') as f:
        mime_type = ReportService.get_mime_type(report.format)
        response = HttpResponse(f.read(), content_type=mime_type)
        preview = request.GET.get('preview') == 'true'
        response['Content-Disposition'] = ReportService.get_disposition(report, preview)
        return response


@login_required
@require_POST
def delete_report(request, report_id):
    report = _get_report_for_user(report_id, request.user)

    ReportService.delete_report_file(report)
    report.delete()

    return redirect('project_detail', pk=report.project.id)
