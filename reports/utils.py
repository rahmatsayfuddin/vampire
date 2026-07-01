import os
from django.template.loader import render_to_string
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
        md_content = render_to_string('reports/report_template.md', context)
        with open(output_path, 'w') as out:
            out.write(md_content)
    else:
        raise ValueError(f"Unsupported format: {format}")

    print("Report generated at:", output_path)
    return filename
