import os
from django.conf import settings
from datetime import datetime


def generate_report_file(project, findings, format='md'):
    context = {
        'project': project,
        'findings': findings,
        'today': datetime.now().date(),
    }

    filename = f"{project.project_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{format}"
    output_path = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if format == 'md':
        template = get_template()

        from django.template import Template, Context
        t = Template(template)
        c = Context(context)
        md_content = t.render(c)

        with open(output_path, 'w') as out:
            out.write(md_content)
    else:
        raise ValueError(f"Unsupported format: {format}")

    print("Report generated at:", output_path)
    return filename


def get_template():
    try:
        from reports.models import ReportTemplate
        obj = ReportTemplate.objects.get(pk=1)
        return obj.content
    except Exception:
        pass

    with open(os.path.join(settings.BASE_DIR, 'reports/templates/reports/report_template.md'), 'r') as f:
        return f.read()
