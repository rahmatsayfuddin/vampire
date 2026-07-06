import csv
import io


def parse_burp(file_path):
    try:
        import lxml.etree as ET
    except ImportError:
        raise ImportError('lxml is required for Burp parsing. Install with: pip install lxml')

    tree = ET.parse(file_path)
    findings = []
    for issue in tree.findall('.//issue'):
        name = (issue.findtext('name') or '').strip()
        sev = (issue.findtext('severity') or 'Info').capitalize()
        path = (issue.findtext('path') or '')
        desc = (issue.findtext('issueBackground') or '')
        remediation = (issue.findtext('remediationBackground') or '')
        if not name:
            continue
        findings.append({
            'title': name,
            'severity': sev,
            'affected': path,
            'description': desc,
            'recommendation': remediation,
        })
    return findings


def parse_csv(file_path):
    findings = []
    with open(file_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get('title') or row.get('Title') or '').strip()
            if not title:
                continue
            sev = (row.get('severity') or row.get('Severity') or 'Info').capitalize()
            findings.append({
                'title': title,
                'severity': sev,
                'affected': (row.get('url') or row.get('URL') or row.get('affected') or ''),
                'description': (row.get('description') or row.get('Description') or ''),
                'recommendation': (row.get('recommendation') or row.get('Recommendation') or ''),
            })
    return findings


PARSERS = {
    'burp': parse_burp,
    'csv': parse_csv,
}
