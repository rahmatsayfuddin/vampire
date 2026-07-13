from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils.timezone import now
from datetime import date, timedelta
from organizations.models import Organization
from projects.models import Project, ScanReport, ScanFinding, ProjectNote, SlaProfile
from findings.models import Finding, FindingComment, RiskAcceptance
from assignments.models import Assignment
from vkb.models import VulnerabilityKnowledgeBase
from reports.models import ReportHistory
from stakeholders.models import Stakeholder


class Command(BaseCommand):
    help = 'Populate database with demo data for multiple scenarios'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning existing data...')
        from django.core.management import call_command
        call_command('clean_data')
        self.stdout.write('')

        sla = self._create_sla()
        orgs = self._create_orgs()
        users = self._create_users()
        projects = self._create_projects(orgs, sla)
        findings = self._create_findings(projects)
        scans = self._create_scans(projects['web_portal'], users['admin'])
        self._create_assignments(projects, users)
        self._create_reports(projects['web_portal'])
        self._create_vkb()
        self._create_stakeholders(projects)
        self._create_notes(projects)

        self.stdout.write(self.style.SUCCESS(
            f'\nDemo data ready!\n'
            f'  Organizations: {len(orgs)}\n'
            f'  SLA Profiles: {len(sla)}\n'
            f'  Users: {len(users)}\n'
            f'  Projects: {len(projects)}\n'
            f'  Findings: {len(findings)} ({self._late_count} late, {self._ra_count} risk-accepted)\n'
            f'  Scan Reports: {len(scans)}\n'
            f'  Login: admin / admin123'
        ))

    def _create_sla(self):
        self.stdout.write('  Creating SLA Profiles...')
        standard = SlaProfile.objects.create(
            name='Standard', description='Default SLA for most projects',
            sla_critical=7, sla_high=14, sla_medium=30, sla_low=60, is_default=True
        )
        critical = SlaProfile.objects.create(
            name='Critical Infrastructure', description='Strict SLA for critical systems',
            sla_critical=3, sla_high=7, sla_medium=14, sla_low=30
        )
        return {'standard': standard, 'critical': critical}

    def _create_orgs(self):
        self.stdout.write('  Creating Organizations...')
        acme = Organization.objects.create(
            name='Acme Corporation', description='E-commerce platform — main pentest target'
        )
        globaltech = Organization.objects.create(
            name='GlobalTech Solutions', description='SaaS provider — quarterly assessments'
        )
        return {'acme': acme, 'globaltech': globaltech}

    def _create_users(self):
        self.stdout.write('  Creating Users...')
        for gname in ['Manager', 'Pentester', 'Viewer']:
            Group.objects.get_or_create(name=gname)
        admin, _ = User.objects.get_or_create(username='admin', defaults={'is_superuser': True, 'is_staff': True})
        if not admin.password:
            admin.set_password('admin123')
            admin.save()
        pentester, _ = User.objects.get_or_create(username='pentester')
        pentester.set_password('demo1234')
        pentester.save()
        pentester.groups.add(Group.objects.get(name='Pentester'))
        viewer, _ = User.objects.get_or_create(username='viewer')
        viewer.set_password('demo1234')
        viewer.save()
        viewer.groups.add(Group.objects.get(name='Viewer'))
        lead, _ = User.objects.get_or_create(username='lead')
        lead.set_password('demo1234')
        lead.save()
        lead.groups.add(Group.objects.get(name='Manager'))
        return {'admin': admin, 'pentester': pentester, 'viewer': viewer, 'lead': lead}

    def _create_projects(self, orgs, sla):
        self.stdout.write('  Creating Projects...')
        today = date.today()

        web_portal = Project.objects.create(
            project_name='Acme Web Portal', organization=orgs['acme'],
            sla_profile=sla['standard'], start_date=today - timedelta(days=21),
            end_date=today + timedelta(days=14), status='In Progress',
            description='Annual penetration test of the public-facing web portal.',
            scope='https://portal.acme.com, https://api.acme.com'
        )
        api_gateway = Project.objects.create(
            project_name='Acme API Gateway', organization=orgs['acme'],
            sla_profile=sla['critical'], start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=7), status='In Progress',
            description='API gateway security review — overdue.',
            scope='https://api-gw.acme.internal'
        )
        legacy = Project.objects.create(
            project_name='Acme Legacy Migration', organization=orgs['acme'],
            sla_profile=sla['standard'],
            start_date=today - timedelta(days=120),
            end_date=today - timedelta(days=30), status='Completed',
            completed_date=today - timedelta(days=30),
            description='Security review during legacy-to-cloud migration.'
        )
        cloud = Project.objects.create(
            project_name='Acme Cloud Infrastructure', organization=orgs['acme'],
            sla_profile=sla['critical'], start_date=today - timedelta(days=90),
            end_date=today + timedelta(days=60), status='On Hold',
            description='Paused — awaiting infra team approval.'
        )
        mobile = Project.objects.create(
            project_name='GlobalTech Mobile App', organization=orgs['globaltech'],
            sla_profile=sla['standard'], start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=7), status='In Progress',
            description='iOS and Android penetration test.'
        )
        network = Project.objects.create(
            project_name='GlobalTech Internal Network', organization=orgs['globaltech'],
            sla_profile=sla['standard'], start_date=today + timedelta(days=30),
            end_date=today + timedelta(days=60), status='Planned',
            description='Internal network segmentation and hardening review.'
        )
        return {
            'web_portal': web_portal, 'api_gateway': api_gateway,
            'legacy': legacy, 'cloud': cloud, 'mobile': mobile, 'network': network
        }

    def _create_findings(self, projects):
        self.stdout.write('  Creating Findings...')
        today = date.today()
        findings = []
        wp = projects['web_portal']
        ag = projects['api_gateway']
        gm = projects['mobile']
        cl = projects['cloud']
        lg = projects['legacy']

        # --- Acme Web Portal (8 findings) ---
        f = Finding.objects.create(project=wp, title='SQL Injection in Login Form', severity='Critical',
            status='Open', affected='https://portal.acme.com/login',
            description='The login form is vulnerable to SQL injection. An attacker can bypass authentication by injecting SQL payloads into the username field.',
            impact='Complete database compromise possible. Attacker can extract user credentials, PII, and session tokens.',
            recommendation='Use parameterized queries or an ORM. Implement input validation and a WAF rule for SQL injection patterns.',
            poc='<p><strong>Proof of Concept</strong></p><pre>POST /login HTTP/1.1<br>username=admin\' OR 1=1--&amp;password=x</pre><p>Result: logged in as admin without valid credentials.</p>',
            created_at=now() - timedelta(days=6))
        findings.append(f)

        Finding.objects.create(project=wp, title='Stored XSS in User Profile', severity='Critical',
            status='Closed', closed_at=now() - timedelta(days=2),
            affected='https://portal.acme.com/profile/edit',
            description='The user profile page does not sanitize input fields.',
            impact='Session hijacking, credential theft, defacement.',
            recommendation='HTML-encode all user input on output.',
            created_at=now() - timedelta(days=5))
        findings.append(f)

        Finding.objects.create(project=wp, title='Missing Rate Limiting on API', severity='High',
            status='Open', affected='https://api.acme.com/v1/auth',
            description='The authentication endpoint lacks rate limiting.',
            impact='Account takeover via credential brute-forcing.',
            recommendation='Implement rate limiting. Add CAPTCHA after 3 failed attempts.',
            created_at=now() - timedelta(days=5))
        findings.append(f)

        Finding.objects.create(project=wp, title='Insecure Direct Object Reference (IDOR)', severity='High',
            status='Risk Acceptance', affected='https://portal.acme.com/invoice/',
            description='Users can access other users\' invoices by modifying the invoice ID.',
            impact='Unauthorized access to financial documents.',
            recommendation='Implement server-side ownership verification.',
            created_at=now() - timedelta(days=4))
        findings.append(f)

        Finding.objects.create(project=wp, title='Sensitive Data in URL Parameters', severity='Medium',
            status='Open', affected='https://portal.acme.com/reset-password',
            description='Password reset tokens passed as URL query parameters.',
            impact='Exposure of reset tokens to browser history and logs.',
            recommendation='Use POST requests with tokens in the request body.',
            created_at=now() - timedelta(days=3))
        findings.append(f)

        Finding.objects.create(project=wp, title='Missing Security Headers', severity='Medium',
            status='Open', affected='https://portal.acme.com',
            description='CSP, HSTS, and X-Frame-Options headers not set.',
            impact='Vulnerable to clickjacking and content injection.',
            recommendation='Add CSP, HSTS, and X-Frame-Options headers.',
            created_at=now() - timedelta(days=3))
        findings.append(f)

        Finding.objects.create(project=wp, title='Verbose Error Messages', severity='Low',
            status='Closed', closed_at=now() - timedelta(days=1),
            affected='https://portal.acme.com/*',
            description='Application returns stack traces in error responses.',
            impact='Information disclosure aiding targeted attacks.',
            recommendation='Configure custom error pages without debugging info.',
            created_at=now() - timedelta(days=2))
        findings.append(f)

        Finding.objects.create(project=wp, title='Missing Autocomplete Attribute', severity='Low',
            status='Open', affected='https://portal.acme.com/login',
            description='Login form does not set autocomplete="off".',
            impact='Cached credentials on shared computers.',
            recommendation='Add autocomplete="off" to sensitive input fields.',
            created_at=now() - timedelta(days=2))
        findings.append(f)

        # --- Acme API Gateway (6 findings) ---
        Finding.objects.create(project=ag, title='JWT Token Without Expiry', severity='Critical',
            status='Open', affected='https://api-gw.acme.internal/auth/token',
            description='JWT tokens issued without expiration claim.',
            impact='Stolen tokens remain valid indefinitely.',
            recommendation='Add exp claim with short lifetime. Implement refresh token rotation.',
            created_at=now() - timedelta(days=6))
        findings.append(f)

        Finding.objects.create(project=ag, title='Unvalidated Redirects', severity='High',
            status='Risk Acceptance', affected='https://api-gw.acme.internal/oauth/callback',
            description='OAuth callback URL not validated against whitelist.',
            impact='Phishing attacks via redirect to malicious domains.',
            recommendation='Validate redirect_uri against registered whitelist.',
            created_at=now() - timedelta(days=5))
        findings.append(f)

        Finding.objects.create(project=ag, title='Insufficient Logging & Monitoring', severity='High',
            status='Open', affected='https://api-gw.acme.internal',
            description='API gateway logs minimal request data. No alerting for suspicious patterns.',
            impact='Security incidents may go undetected.',
            recommendation='Implement structured logging with correlation IDs and alerts.',
            created_at=now() - timedelta(days=5))
        findings.append(f)

        Finding.objects.create(project=ag, title='Missing CORS Configuration', severity='Medium',
            status='Closed', closed_at=now() - timedelta(days=3),
            affected='https://api-gw.acme.internal',
            description='CORS set to Access-Control-Allow-Origin: *.',
            impact='Any website can make authenticated cross-origin requests.',
            recommendation='Restrict CORS to trusted origins only.',
            created_at=now() - timedelta(days=3))
        findings.append(f)

        Finding.objects.create(project=ag, title='TLS 1.0/1.1 Enabled', severity='Medium',
            status='Open', affected='https://api-gw.acme.internal:443',
            description='Server supports deprecated TLS 1.0 and 1.1.',
            impact='Vulnerable to POODLE and TLS downgrade attacks.',
            recommendation='Disable TLS 1.0/1.1. Enforce TLS 1.2 minimum.',
            created_at=now() - timedelta(days=3))
        findings.append(f)

        Finding.objects.create(project=ag, title='Server Information Disclosure', severity='Low',
            status='Closed', closed_at=now() - timedelta(days=2),
            affected='https://api-gw.acme.internal',
            description='Server header reveals Apache and PHP versions.',
            impact='Attackers can target version-specific vulnerabilities.',
            recommendation='Configure ServerTokens Prod and expose_php Off.',
            created_at=now() - timedelta(days=2))
        findings.append(f)

        # --- GlobalTech Mobile App (5 findings) ---
        Finding.objects.create(project=gm, title='Hardcoded API Key', severity='Critical',
            status='Open', affected='com.globaltech.app.config',
            description='API key hardcoded in mobile app binary.',
            impact='Full backend compromise via extracted API key.',
            recommendation='Move API keys to server-side. Use OAuth2 with PKCE.',
            created_at=now() - timedelta(days=5))
        findings.append(f)

        Finding.objects.create(project=gm, title='Certificate Pinning Not Implemented', severity='High',
            status='Open', affected='api.globaltech.com',
            description='Mobile app does not implement SSL certificate pinning.',
            impact='TLS traffic can be intercepted on compromised networks.',
            recommendation='Implement certificate pinning via Network Security Config.',
            created_at=now() - timedelta(days=4))
        findings.append(f)

        Finding.objects.create(project=gm, title='Unencrypted Local Storage', severity='Medium',
            status='Open', affected='app://local/shared_prefs',
            description='User session tokens stored in cleartext in SharedPreferences.',
            impact='Token extraction via physical access or malware.',
            recommendation='Use EncryptedSharedPreferences or Android Keystore.',
            created_at=now() - timedelta(days=3))
        findings.append(f)

        Finding.objects.create(project=gm, title='Insecure WebView Configuration', severity='Medium',
            status='Risk Acceptance', affected='com.globaltech.app.WebViewActivity',
            description='WebView has JavaScript enabled with untrusted URLs.',
            impact='JavaScript injection within the app context.',
            recommendation='Disable JavaScript unless required. Whitelist loaded URLs.',
            created_at=now() - timedelta(days=3))
        findings.append(f)

        Finding.objects.create(project=gm, title='Debug Logging in Release Build', severity='Low',
            status='Open', affected='com.globaltech.app',
            description='Sensitive data logged via Log.d() in production builds.',
            impact='Data leakage via logcat on rooted devices.',
            recommendation='Remove all debug logging in release builds.',
            created_at=now() - timedelta(days=2))
        findings.append(f)

        # --- Other projects ---
        Finding.objects.create(project=cl, title='Unpatched OS Vulnerabilities', severity='Critical',
            status='Open', affected='10.0.0.5-10.0.0.25',
            description='Multiple VMs running outdated OS versions with known CVEs.',
            impact='Lateral movement and privilege escalation.',
            recommendation='Apply latest security patches.',
            created_at=now() - timedelta(days=5))
        findings.append(f)

        Finding.objects.create(project=cl, title='Open S3 Bucket', severity='High',
            status='Open', affected='s3://acme-backups',
            description='S3 bucket containing database backups is publicly accessible.',
            impact='Full data exposure of production database backups.',
            recommendation='Enable bucket ACL to private. Enable Block Public Access.',
            created_at=now() - timedelta(days=5))
        findings.append(f)

        Finding.objects.create(project=lg, title='Default Admin Credentials', severity='Critical',
            status='Closed', closed_at=now() - timedelta(days=5),
            affected='admin.acme-internal.com',
            description='Default admin/admin credentials found on legacy admin panel.',
            impact='Full administrative access to legacy system.',
            recommendation='Changed default credentials. Implemented SSO.',
            created_at=now() - timedelta(days=5))
        findings.append(f)

        Finding.objects.create(project=lg, title='Unencrypted Database Connection', severity='High',
            status='Closed', closed_at=now() - timedelta(days=4),
            affected='legacy-db.acme-internal.com:3306',
            description='Database connections use plaintext without TLS.',
            impact='MITM interception of database traffic.',
            recommendation='Enabled TLS on all database connections.',
            created_at=now() - timedelta(days=5))
        findings.append(f)

        Finding.objects.create(project=lg, title='Outdated Library Versions', severity='Medium',
            status='Closed', closed_at=now() - timedelta(days=3),
            affected='legacy.acme-internal.com',
            description='Multiple outdated libraries with known CVEs.',
            impact='Remote code execution via known library exploits.',
            recommendation='Updated all libraries to latest stable versions.',
            created_at=now() - timedelta(days=3))
        findings.append(f)

        # Force a few specific findings to be late
        for title_prefix in ['SQL Injection in Login', 'JWT Token', 'Hardcoded API Key', 'Unpatched OS', 'Insufficient Logging']:
            Finding.objects.filter(title__startswith=title_prefix).update(
                created_at=now() - timedelta(days=365)
            )
        ra_count = Finding.objects.filter(status='Risk Acceptance').count()
        for f in Finding.objects.filter(status='Risk Acceptance'):
            RiskAcceptance.objects.create(
                finding=f, reason='Business accepted risk — fix planned for next quarter',
                evidence='Risk acceptance form signed by CISO',
                accepted_by=User.objects.get(username='lead'),
                accepted_at=now() - timedelta(days=2),
                accept_until=today + timedelta(days=90)
            )
        late_count = sum(1 for f in Finding.objects.all() if f.is_late())
        self._late_count = late_count
        self._ra_count = ra_count
        return findings

    def _create_scans(self, project, uploader):
        self.stdout.write('  Creating Scan Reports...')
        today = date.today()

        r1 = ScanReport.objects.create(
            project=project, source_tool='nessus', file='scans/nessus_scan1.nessus',
            uploaded_by=uploader, status='done',
            uploaded_at=today - timedelta(days=10)
        )
        # Scan 1 findings
        ScanFinding.objects.create(report=r1, title='SQL Injection in Login', severity='Critical',
            affected='portal.acme.com / 10.0.1.5:443 (https)', description='SQL injection confirmed via automated scan.',
            recommendation='Use parameterized queries.')
        ScanFinding.objects.create(report=r1, title='Stored XSS in Profile', severity='Critical',
            affected='portal.acme.com / 10.0.1.5:443', description='Stored XSS in user profile bio field.')
        ScanFinding.objects.create(report=r1, title='Missing Rate Limiting', severity='High',
            affected='api.acme.com / 10.0.1.10:443', description='No rate limiting on login endpoint.')
        ScanFinding.objects.create(report=r1, title='IDOR in Invoice API', severity='High',
            affected='portal.acme.com / 10.0.1.5:443', description='Direct object reference on invoice IDs.')
        ScanFinding.objects.create(report=r1, title='Sensitive Data in URL', severity='Medium',
            affected='portal.acme.com / 10.0.1.5:443', description='Tokens in URL parameters.')
        ScanFinding.objects.create(report=r1, title='Missing CSP Header', severity='Medium',
            affected='portal.acme.com / 10.0.1.5:443', description='No Content-Security-Policy header.')
        ScanFinding.objects.create(report=r1, title='Verbose Error Messages', severity='Low',
            affected='portal.acme.com / 10.0.1.5:443', description='Stack traces exposed.')
        ScanFinding.objects.create(report=r1, title='Missing HSTS Header', severity='Low',
            affected='portal.acme.com / 10.0.1.5:443', description='HSTS not configured.')
        ScanFinding.objects.create(report=r1, title='Autocomplete Not Disabled', severity='Low',
            affected='portal.acme.com / 10.0.1.5:443', description='Browser credential caching.')

        r2 = ScanReport.objects.create(
            project=project, source_tool='nessus', file='scans/nessus_scan2.nessus',
            uploaded_by=uploader, status='done',
            uploaded_at=today - timedelta(days=3)
        )
        # Scan 2 — after some fixes
        ScanFinding.objects.create(report=r2, title='SQL Injection in Login', severity='Critical',
            affected='portal.acme.com / 10.0.1.5:443', description='SQL injection still present in login form.')
        ScanFinding.objects.create(report=r2, title='Missing Rate Limiting', severity='High',
            affected='api.acme.com / 10.0.1.10:443', description='Rate limiting still not implemented.')
        ScanFinding.objects.create(report=r2, title='New: CSRF in Admin Panel', severity='High',
            affected='admin.acme.com / 10.0.1.5:8443', description='Admin panel lacks CSRF tokens.')
        ScanFinding.objects.create(report=r2, title='New: Open S3 Bucket', severity='Critical',
            affected='s3://acme-assets', description='Publicly accessible asset bucket found.')
        ScanFinding.objects.create(report=r2, title='Sensitive Data in URL', severity='Medium',
            affected='portal.acme.com / 10.0.1.5:443', description='Tokens in URL parameters still present.')
        ScanFinding.objects.create(report=r2, title='Missing CSP Header', severity='Medium',
            affected='portal.acme.com / 10.0.1.5:443', description='CSP still not configured.')
        ScanFinding.objects.create(report=r2, title='Missing HSTS Header', severity='Low',
            affected='portal.acme.com / 10.0.1.5:443', description='HSTS not added yet.')

        r3 = ScanReport.objects.create(
            project=project, source_tool='burp', file='scans/burp_portal.xml',
            uploaded_by=uploader, status='done',
            uploaded_at=today - timedelta(days=5)
        )
        ScanFinding.objects.create(report=r3, title='SQL Injection (Burp)', severity='Critical',
            affected='https://portal.acme.com/login', description='Confirmed via Burp Scanner.')
        ScanFinding.objects.create(report=r3, title='Stored XSS (Burp)', severity='Critical',
            affected='https://portal.acme.com/profile', description='Detected by Burp active scan.')
        ScanFinding.objects.create(report=r3, title='CSRF Token Missing', severity='High',
            affected='https://portal.acme.com/settings', description='Form lacks CSRF protection.')
        ScanFinding.objects.create(report=r3, title='Directory Listing', severity='Medium',
            affected='https://portal.acme.com/assets/', description='Directory listing enabled.')
        ScanFinding.objects.create(report=r3, title='Insecure Cookie Flags', severity='Low',
            affected='https://portal.acme.com', description='Cookies missing Secure and HttpOnly flags.')

        return [r1, r2, r3]

    def _create_assignments(self, projects, users):
        self.stdout.write('  Creating Assignments...')
        Assignment.objects.create(project=projects['web_portal'], user=users['lead'], title='Lead Pentester')
        Assignment.objects.create(project=projects['web_portal'], user=users['pentester'], title='Web Pentester')
        Assignment.objects.create(project=projects['api_gateway'], user=users['lead'], title='Lead Pentester')
        Assignment.objects.create(project=projects['api_gateway'], user=users['pentester'], title='API Security Specialist')
        Assignment.objects.create(project=projects['mobile'], user=users['lead'], title='Lead Pentester')
        Assignment.objects.create(project=projects['mobile'], user=users['pentester'], title='Mobile Pentester')
        Assignment.objects.create(project=projects['cloud'], user=users['admin'], title='Cloud Security Engineer')
        Assignment.objects.create(project=projects['legacy'], user=users['admin'], title='Lead Pentester')
        Assignment.objects.create(project=projects['network'], user=users['admin'], title='Project Owner')
        Assignment.objects.create(project=projects['network'], user=users['viewer'], title='Observer')

    def _create_reports(self, project):
        self.stdout.write('  Creating Report History...')
        ReportHistory.objects.create(project=project, file_name='acme_web_portal_report.md',
            format='md', status='done', created_at=now() - timedelta(days=2))
        ReportHistory.objects.create(project=project, file_name='acme_web_portal_draft.md',
            format='md', status='failed', created_at=now() - timedelta(days=5))

    def _create_vkb(self):
        self.stdout.write('  Creating VKB Entries...')
        vkb_data = [
            ('SQL Injection', 'Injection', 'User-supplied input is interpreted as SQL commands, allowing attackers to manipulate database queries.',
             'Unauthorized data access, data modification, and in some cases remote code execution.',
             'Use parameterized queries, ORM frameworks, and input validation.'),
            ('Cross-Site Scripting (XSS)', 'Injection', 'Untrusted data is sent to the browser without proper validation or escaping.',
             'Session hijacking, credential theft, website defacement, and malware distribution.',
             'HTML-encode all user-generated content. Implement Content-Security-Policy headers.'),
            ('Cross-Site Request Forgery (CSRF)', 'Broken Access Control', 'An attacker tricks a user into performing unwanted actions on a trusted website.',
             'Unauthorized fund transfers, password changes, and data modification.',
             'Implement anti-CSRF tokens. Validate Referer/Origin headers. Use SameSite cookie attribute.'),
            ('Server-Side Request Forgery (SSRF)', 'Broken Access Control', 'The server is tricked into making requests to unintended locations, such as internal services.',
             'Access to internal systems, cloud metadata services, and sensitive data exfiltration.',
             'Validate and sanitize user-supplied URLs. Use allowlists for outbound connections.'),
            ('Authentication Bypass', 'Identification and Authentication Failures', 'Weaknesses in authentication mechanisms that allow attackers to impersonate users.',
             'Account takeover, unauthorized access to sensitive functionality.',
             'Implement multi-factor authentication. Enforce strong password policies. Rate-limit login attempts.'),
            ('Information Disclosure', 'Security Misconfiguration', 'Sensitive information is unintentionally exposed to users or attackers.',
             'System fingerprinting, targeted attacks based on version information.',
             'Disable detailed error messages in production. Remove or restrict access to sensitive files and directories.'),
            ('Privilege Escalation', 'Broken Access Control', 'Users can access functionality or data beyond their intended permissions.',
             'Unauthorized access to admin functions, data breaches.',
             'Implement proper role-based access control. Verify permissions on every request.'),
            ('Insecure Deserialization', 'Software and Data Integrity Failures', 'Untrusted data is deserialized without proper validation, leading to object injection.',
             'Remote code execution, denial of service, authentication bypass.',
             'Avoid deserializing untrusted data. Use integrity checks. Implement allowlists for deserialized types.'),
        ]
        for title, cat, desc, impact, rec in vkb_data:
            VulnerabilityKnowledgeBase.objects.create(
                title=title, category=cat, description=desc, impact=impact, recommendation=rec
            )

    def _create_stakeholders(self, projects):
        self.stdout.write('  Creating Stakeholders...')
        Stakeholder.objects.create(project=projects['web_portal'], name='Sarah Chen',
            email='sarah.chen@acme.com', position='CTO')
        Stakeholder.objects.create(project=projects['web_portal'], name='Mike Johnson',
            email='mike.johnson@acme.com', position='Dev Lead')
        Stakeholder.objects.create(project=projects['mobile'], name='Alex Rivera',
            email='alex.rivera@globaltech.com', position='Mobile Engineering Manager')
        Stakeholder.objects.create(project=projects['cloud'], name='David Park',
            email='david.park@acme.com', position='Infrastructure Director')

    def _create_notes(self, projects):
        self.stdout.write('  Creating Project Notes...')
        from projects.models import ProjectNote
        admin = User.objects.get(username='admin')
        ProjectNote.objects.create(project=projects['web_portal'],
            user=admin, content='Kickoff meeting held with dev team. Scope confirmed: web portal + API.',
            created_at=now() - timedelta(days=20))
        ProjectNote.objects.create(project=projects['web_portal'],
            user=admin, content='Nessus scan completed — 8 findings. Critical SQLi and XSS confirmed.',
            created_at=now() - timedelta(days=8))
        ProjectNote.objects.create(project=projects['web_portal'],
            user=admin, content='Second Nessus scan shows Stored XSS resolved (not in scan 2). New CSRF issue found on admin panel. S3 bucket exposure identified.',
            created_at=now() - timedelta(days=2))
        ProjectNote.objects.create(project=projects['api_gateway'],
            user=admin, content='API Gateway review started. JWT token issues and TLS configuration are top priority.',
            created_at=now() - timedelta(days=55))
        ProjectNote.objects.create(project=projects['api_gateway'],
            user=admin, content='SLA overdue — escalated to project manager. Critical JWT finding still open.',
            created_at=now() - timedelta(days=3))
