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
        sev_raw = (issue.findtext('severity') or 'Info')
        if sev_raw in ('Information', 'Info', 'info'):
            continue
        name = (issue.findtext('name') or '').strip()
        host_elem = issue.find('host')
        host_ip = host_elem.get('ip', '') if host_elem is not None else ''
        host_name = (host_elem.text or '').strip() if host_elem is not None else ''
        path = (issue.findtext('path') or '').strip()

        affected = host_name or host_ip
        if path:
            affected += path

        findings.append({
            'title': name,
            'severity': sev_raw.capitalize(),
            'affected': affected,
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
    risk_map = {'1': 'Low', '2': 'Medium', '3': 'High'}
    findings = []
    for alert in tree.findall('.//alertitem'):
        riskcode = alert.findtext('riskcode', '0')
        sev = risk_map.get(riskcode)
        if sev is None:
            continue
        name = (alert.findtext('alert') or '').strip()
        uri = (alert.findtext('uri') or '').strip()

        findings.append({
            'title': name,
            'severity': sev,
            'affected': uri,
            'description': (alert.findtext('desc') or '').strip(),
            'recommendation': (alert.findtext('solution') or '').strip(),
        })
    return findings


def parse_nessus(file_path):
    ET = _get_et()
    is_nessus_xml = False
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        is_nessus_xml = root.tag in ('NessusClientData_v2', 'NessusClientData')
    except Exception:
        pass

    if is_nessus_xml:
        return _parse_nessus_xml(file_path)

    try:
        return _parse_nessus_csv(file_path)
    except Exception:
        pass

    return []


def _parse_nessus_xml(file_path):
    ET = _get_et()
    tree = ET.parse(file_path)
    sev_map = {'1': 'Low', '2': 'Medium', '3': 'High', '4': 'Critical'}
    findings = []

    for host in tree.iter('ReportHost'):
        host_name = host.get('name', '')
        host_ip = host_name
        props = host.find('HostProperties')
        if props is not None:
            for tag in props.findall('tag'):
                if tag.get('name') == 'host-ip':
                    host_ip = tag.text or host_name
                    break

        for item in host.findall('ReportItem'):
            name = item.get('pluginName', '')
            if not name or name == 'Nessus Scan Information':
                continue

            sev = sev_map.get(item.get('severity', '0'))
            if sev is None:
                continue

            port = item.get('port', '0')
            protocol = item.get('protocol', '')
            svc = item.get('svc_name', '')
            affected_parts = [host_name]
            if host_ip and host_ip != host_name:
                affected_parts.append(host_ip)
            affected = ' / '.join(affected_parts)
            if port != '0':
                affected += f':{port}'
            if svc and svc != 'general':
                affected += f' ({svc})'

            desc = item.findtext('description', '')
            evidence = item.findtext('plugin_output', '')
            if evidence:
                desc = (desc or '') + '\n\n--- Evidence ---\n' + evidence

            solution = item.findtext('solution', '')
            if solution == 'n/a':
                solution = ''

            findings.append({
                'title': name,
                'severity': sev,
                'affected': affected,
                'description': desc.strip(),
                'recommendation': solution.strip(),
            })

    return findings


def _parse_nessus_csv(file_path):
    findings = []
    with open(file_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = [h.lower() for h in (reader.fieldnames or [])]

        if 'ip address' in headers or 'ip' in headers:
            return _parse_nessus_csv_vuln_list(reader, headers)
        elif 'total' in headers and 'host total' in headers:
            return _parse_nessus_csv_summary(reader)
    return findings


def _parse_nessus_csv_vuln_list(reader, headers):
    groups = {}
    for row in reader:
        pid = row.get('Plugin', '') or row.get('Plugin ID', '')
        name = row.get('Plugin Name', '') or row.get('Name', '')
        sev = row.get('Severity', '') or row.get('Risk', '')
        ip_col = 'IP Address' if 'IP Address' in reader.fieldnames else ('IP' if 'IP' in reader.fieldnames else None)
        ip = row.get(ip_col, '') if ip_col else ''
        if not pid or not name:
            continue
        key = pid
        if key not in groups:
            groups[key] = {'name': name.strip(), 'severity': sev.strip(), 'ips': []}
        if ip:
            groups[key]['ips'].append(ip.strip())

    result = []
    for pid, g in groups.items():
        ips = sorted(set(g['ips']))
        desc = f'Affected hosts: {len(ips)}\n\n' + '\n'.join(ips) if ips else 'No host IP detail available.'
        result.append({
            'title': g['name'],
            'severity': g['severity'],
            'affected': ', '.join(ips[:5]) + ('...' if len(ips) > 5 else ''),
            'description': desc,
            'recommendation': '',
        })
    return result


def _parse_nessus_csv_summary(reader):
    findings = []
    for row in reader:
        name = row.get('Plugin Name', '') or row.get('Name', '')
        sev = row.get('Severity', '') or ''
        host_total = row.get('Host Total', '') or row.get('Total', '0')
        if not name:
            continue
        findings.append({
            'title': name.strip(),
            'severity': sev.strip(),
            'affected': '',
            'description': f'Total hosts affected: {host_total}',
            'recommendation': '',
        })
    return findings


def parse_acunetix(file_path):
    ET = _get_et()
    tree = ET.parse(file_path)
    findings = []
    for item in tree.findall('.//ReportItem'):
        sev_raw = (item.findtext('Severity') or 'medium').strip().lower()
        if sev_raw in ('informational', 'info'):
            continue
        sev_map = {'high': 'High', 'medium': 'Medium', 'low': 'Low', 'critical': 'Critical'}
        name = (item.findtext('Name') or '').strip()
        if not name:
            continue
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
    for host in tree.findall('.//host'):
        address = host.find('address')
        host_ip = address.get('addr', '') if address is not None else ''
        hostnames = host.find('hostnames')
        host_name = ''
        if hostnames is not None:
            hn = hostnames.find('hostname')
            if hn is not None:
                host_name = hn.get('name', '')

        for port in host.findall('.//port'):
            state = port.find('state')
            if state is None or state.get('state') != 'open':
                continue
            protocol = port.get('protocol', '')
            portid = port.get('portid', '')
            service = port.find('service')
            svc_name = (service.get('name', 'unknown') if service is not None else 'unknown')
            product = (service.get('product', '') if service is not None else '')

            title = f'{svc_name} ({portid}/{protocol})'
            if product:
                title += f' - {product}'

            affected = host_ip
            if host_name:
                affected = f'{host_name} ({host_ip})'
            affected += f':{portid}/{protocol}'

            findings.append({
                'title': title,
                'severity': 'Info',
                'affected': affected,
                'description': f'Open port {portid}/{protocol}: {svc_name}' + (f' ({product})' if product else ''),
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
