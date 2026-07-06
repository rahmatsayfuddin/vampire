import csv
import io
import re


def _get_et():
    try:
        import lxml.etree as ET
        return ET
    except ImportError:
        raise ImportError('lxml required. Install: pip install lxml')


def parse_burp(file_path):
    ET = _get_et()
    tree = ET.parse(file_path)
    findings = []
    for issue in tree.findall('.//issue'):
        name = (issue.findtext('name') or '').strip()
        sev = (issue.findtext('severity') or 'Info').capitalize()
        findings.append({
            'title': name,
            'severity': sev,
            'affected': (issue.findtext('path') or ''),
            'description': (issue.findtext('issueBackground') or ''),
            'recommendation': (issue.findtext('remediationBackground') or ''),
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


def parse_zap(file_path):
    ET = _get_et()
    tree = ET.parse(file_path)
    risk_map = {'0': 'Info', '1': 'Low', '2': 'Medium', '3': 'High'}
    findings = []
    for alert in tree.findall('.//alertitem'):
        name = (alert.findtext('alert') or '').strip()
        if not name:
            continue
        riskcode = alert.findtext('riskcode', '0')
        findings.append({
            'title': name,
            'severity': risk_map.get(riskcode, 'Info'),
            'affected': (alert.findtext('uri') or ''),
            'description': (alert.findtext('desc') or '').strip(),
            'recommendation': (alert.findtext('solution') or '').strip(),
        })
    return findings


def parse_nessus(file_path):
    ET = _get_et()
    tree = ET.parse(file_path)
    sev_map = {'0': 'Info', '1': 'Low', '2': 'Medium', '3': 'High', '4': 'Critical'}
    findings = []
    for item in tree.iter('ReportItem'):
        name = item.get('pluginName', '')
        if not name or name == 'Nessus Scan Information':
            continue
        findings.append({
            'title': name,
            'severity': sev_map.get(item.get('severity', '0'), 'Info'),
            'affected': item.get('svc_name', ''),
            'description': (item.findtext('plugin_output', '') or ''),
            'recommendation': (item.findtext('solution', '') or ''),
        })
    return findings


def parse_acunetix(file_path):
    ET = _get_et()
    tree = ET.parse(file_path)
    findings = []
    for item in tree.findall('.//ReportItem'):
        name = (item.findtext('Name') or '').strip()
        if not name:
            continue
        sev_raw = (item.findtext('Severity') or 'medium').strip().lower()
        sev_map = {'high': 'High', 'medium': 'Medium', 'low': 'Low', 'critical': 'Critical', 'info': 'Info'}
        findings.append({
            'title': name,
            'severity': sev_map.get(sev_raw, 'Info'),
            'affected': (item.findtext('Affects') or ''),
            'description': (item.findtext('Description') or ''),
            'recommendation': (item.findtext('Recommendation') or ''),
        })
    return findings


def parse_nmap(file_path):
    ET = _get_et()
    tree = ET.parse(file_path)
    findings = []
    for port in tree.findall('.//port'):
        protocol = port.get('protocol', '')
        portid = port.get('portid', '')
        service = port.find('service')
        state = port.find('state')
        if state is None or state.get('state') != 'open':
            continue
        service_name = (service.get('name', 'unknown') if service is not None else 'unknown')
        product = (service.get('product', '') if service is not None else '')
        title = f'{service_name} ({portid}/{protocol})'
        if product:
            title += f' — {product}'
        findings.append({
            'title': title,
            'severity': 'Info',
            'affected': f'{portid}/{protocol}',
            'description': f'Open port {portid}/{protocol}: {service_name}' + (f' ({product})' if product else ''),
            'recommendation': 'Review if port is required and properly secured.',
        })
    return findings


def parse_openvas_csv(file_path):
    findings = []
    with open(file_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = (row.get('name') or row.get('Name') or row.get('title') or '').strip()
            if not title:
                continue
            sev_raw = (row.get('severity') or row.get('Severity') or '0').strip()
            try:
                sev_val = float(sev_raw)
                if sev_val >= 7.0:
                    sev = 'High'
                elif sev_val >= 4.0:
                    sev = 'Medium'
                elif sev_val > 0:
                    sev = 'Low'
                else:
                    sev = 'Info'
            except ValueError:
                sev = sev_raw.capitalize() if sev_raw.lower() in ('critical','high','medium','low') else 'Info'
            findings.append({
                'title': title,
                'severity': sev,
                'affected': (row.get('host') or row.get('ip') or row.get('Host') or ''),
                'description': (row.get('description') or row.get('Description') or ''),
                'recommendation': (row.get('solution') or row.get('Solution') or row.get('recommendation') or ''),
            })
    return findings


PARSERS = {
    'burp': parse_burp,
    'csv': parse_csv,
    'zap': parse_zap,
    'nessus': parse_nessus,
    'acunetix': parse_acunetix,
    'nmap': parse_nmap,
    'openvas': parse_openvas_csv,
}
