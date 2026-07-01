from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta, datetime
from organizations.models import Organization
from projects.models import Project, SlaProfile
from findings.models import Finding
from findings.services import SlaService
from projects.services import ProjectMetricsService


class SlaServiceTest(TestCase):

    def setUp(self):
        self.org = Organization.objects.create(name='SLA Test Org')
        standard = SlaProfile.objects.create(name='Standard', is_default=True, sla_critical=7, sla_high=14, sla_medium=30, sla_low=60)
        fast = SlaProfile.objects.create(name='Fast', sla_critical=3, sla_high=5, sla_medium=10, sla_low=20)
        self.proj_standard = Project.objects.create(
            project_name='SLA Std', organization=self.org, sla_profile=standard,
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), status='In Progress'
        )
        self.proj_fast = Project.objects.create(
            project_name='SLA Fast', organization=self.org, sla_profile=fast,
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), status='In Progress'
        )
        self.proj_none = Project.objects.create(
            project_name='SLA None', organization=self.org,
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), status='In Progress'
        )

    def _make_finding(self, project, severity='Critical', status='Open', days_ago=0):
        finding = Finding.objects.create(
            project=project, title='Test', description='D', impact='I',
            recommendation='R', severity=severity, status=status
        )
        if days_ago:
            finding.created_at = timezone.now() - timedelta(days=days_ago)
            finding.save(update_fields=['created_at'])
        return finding

    def test_sla_days_with_profile(self):
        f = self._make_finding(self.proj_fast, 'Critical')
        self.assertEqual(SlaService.sla_days(f), 3)
        f.severity = 'Medium'
        self.assertEqual(SlaService.sla_days(f), 10)

    def test_sla_days_default_fallback(self):
        f = self._make_finding(self.proj_none, 'Critical')
        self.assertEqual(SlaService.sla_days(f), 7)
        f.severity = 'Low'
        self.assertEqual(SlaService.sla_days(f), 60)

    def test_sla_due_date(self):
        f = self._make_finding(self.proj_fast, 'Critical')
        expected = f.created_at + timedelta(days=3)
        self.assertEqual(SlaService.sla_due_date(f).date(), expected.date())

    def test_is_late_open_finding(self):
        f = self._make_finding(self.proj_fast, 'Critical', days_ago=5)
        self.assertTrue(SlaService.is_late(f))

    def test_is_late_open_within_sla(self):
        f = self._make_finding(self.proj_fast, 'Critical', days_ago=1)
        self.assertFalse(SlaService.is_late(f))

    def test_is_late_closed_late(self):
        past = timezone.now() - timedelta(days=10)
        f = self._make_finding(self.proj_fast, 'Critical', status='Closed')
        f.created_at = past - timedelta(days=5)
        f.closed_at = past
        f.save(update_fields=['created_at', 'closed_at'])
        self.assertTrue(SlaService.is_late(f))

    def test_is_late_closed_on_time(self):
        f = self._make_finding(self.proj_fast, 'Critical', status='Closed')
        f.closed_at = f.created_at + timedelta(days=1)
        f.save(update_fields=['closed_at'])
        self.assertFalse(SlaService.is_late(f))

    def test_sla_delay_days(self):
        f = self._make_finding(self.proj_fast, 'Critical', days_ago=5)
        self.assertEqual(SlaService.sla_delay_days(f), 2)

    def test_sla_delay_days_not_late(self):
        f = self._make_finding(self.proj_fast, 'Critical', days_ago=1)
        self.assertEqual(SlaService.sla_delay_days(f), 0)


class ProjectMetricsTest(TestCase):

    def setUp(self):
        self.org = Organization.objects.create(name='SPI Test Org')

    def _make_project(self, start, end, completed=None, status='In Progress'):
        return Project.objects.create(
            project_name=f'SPI {start}-{end}',
            organization=self.org,
            start_date=start,
            end_date=end,
            completed_date=completed,
            status=status,
        )

    def test_spi_on_track(self):
        proj = self._make_project(date(2026, 1, 1), date(2026, 12, 31))
        now = datetime(2026, 7, 1, 0, 0, 0)
        spi = ProjectMetricsService.spi(proj, now=now)
        self.assertAlmostEqual(spi, 2.01, places=1)

    def test_spi_completed_fast(self):
        proj = self._make_project(date(2026, 1, 1), date(2026, 12, 31), completed=date(2026, 3, 1), status='Completed')
        spi = ProjectMetricsService.spi(proj)
        self.assertAlmostEqual(spi, 6.20, places=1)

    def test_spi_missing_dates(self):
        from projects.models import Project
        proj = Project(project_name='No dates', organization=self.org, status='Planned')
        self.assertIsNone(ProjectMetricsService.spi(proj))

    def test_spi_zero_duration(self):
        proj = self._make_project(date(2026, 1, 1), date(2026, 1, 1))
        self.assertIsNone(ProjectMetricsService.spi(proj))
