from django.core.management.base import BaseCommand
from organizations.models import Organization
from projects.models import Project, ScanReport, ScanFinding, ProjectNote, SlaProfile
from findings.models import Finding, FindingComment, RiskAcceptance
from assignments.models import Assignment
from vkb.models import VulnerabilityKnowledgeBase
from reports.models import ReportHistory, ReportTemplate
from stakeholders.models import Stakeholder
from audit.models import AuditLog


class Command(BaseCommand):
    help = 'Clean all application data except Users and Groups'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning data...')
        ReportHistory.objects.all().delete()
        ReportTemplate.objects.all().delete()
        AuditLog.objects.all().delete()
        FindingComment.objects.all().delete()
        RiskAcceptance.objects.all().delete()
        Finding.objects.all().delete()
        ScanFinding.objects.all().delete()
        ScanReport.objects.all().delete()
        ProjectNote.objects.all().delete()
        Assignment.objects.all().delete()
        Stakeholder.objects.all().delete()
        Project.objects.all().delete()
        SlaProfile.objects.all().delete()
        VulnerabilityKnowledgeBase.objects.all().delete()
        Organization.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All application data cleaned (Users & Groups preserved)'))
