from django.core.management.base import BaseCommand
from products.models import Product
from projects.models import Project
from findings.models import Finding
from assignments.models import Assignment
from vkb.models import VulnerabilityKnowledgeBase
from reports.models import ReportHistory
from stakeholders.models import Stakeholder

class Command(BaseCommand):
    help = 'Clean all data except Users and Groups for E2E testing'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning data...')

        # Delete in order of dependencies (though CASCADE should handle most)
        
        # Reports
        ReportHistory.objects.all().delete()
        self.stdout.write('Deleted Reports')

        # Findings
        Finding.objects.all().delete()
        self.stdout.write('Deleted Findings')

        # Assignments
        Assignment.objects.all().delete()
        self.stdout.write('Deleted Assignments')

        # Projects
        Project.objects.all().delete()
        self.stdout.write('Deleted Projects')

        # Products
        Product.objects.all().delete()
        self.stdout.write('Deleted Products')

        # VKB
        VulnerabilityKnowledgeBase.objects.all().delete()
        self.stdout.write('Deleted VKB')

        # Stakeholders
        Stakeholder.objects.all().delete()
        self.stdout.write('Deleted Stakeholders')

        self.stdout.write(self.style.SUCCESS('Successfully cleaned all application data (Users preserved)'))
