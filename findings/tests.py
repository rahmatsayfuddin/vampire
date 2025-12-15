from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from organizations.models import Organization
from projects.models import Project
from findings.models import Finding
from assignments.models import Assignment
from django.utils import timezone
import datetime

class FindingListViewTest(TestCase):
    def setUp(self):
        # Create users
        self.superuser = User.objects.create_superuser('admin', '[email protected]', 'password')
        self.user = User.objects.create_user('user', '[email protected]', 'password')
        
        # Setup roles (simulated)
        group = Group.objects.create(name='Pentester')
        # Assign permissions to group
        from django.contrib.auth.models import Permission
        view_finding = Permission.objects.get(codename='view_finding')
        group.permissions.add(view_finding)
        self.user.groups.add(group)

        # Create data
        self.org = Organization.objects.create(name='Test Org')
        self.project = Project.objects.create(
            project_name='Test Project',
            organization=self.org,
            status='Planned',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + datetime.timedelta(days=30)
        )
        
        # Create 15 findings
        for i in range(15):
            Finding.objects.create(
                project=self.project,
                title=f'Finding {i}',
                description='Desc',
                impact='High',
                severity='High',
                status='Open'
            )
            
        # Assign user to project
        Assignment.objects.create(project=self.project, user=self.user, title='Tester')

    def test_pagination_superuser(self):
        self.client.force_login(self.superuser)
        response = self.client.get('/findings/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context or 'page_obj' in response.context)
        # Should show 10 items on first page
        self.assertEqual(len(response.context['page_obj']), 10)
        
        response = self.client.get('/findings/?page=2')
        self.assertEqual(response.status_code, 200)
        # Should show 5 items on second page
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_user_access(self):
        self.client.force_login(self.user)
        response = self.client.get('/findings/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_unassigned_project_access(self):
        # Create another project and finding unassigned to user
        project2 = Project.objects.create(
             project_name='Other Project',
             organization=self.org,
             status='Planned',
             start_date=timezone.now().date(),
             end_date=timezone.now().date() + datetime.timedelta(days=30)
        )
        Finding.objects.create(
            project=project2,
            title='Secret Finding',
            description='Desc',
            impact='High',
            severity='Critical',
            status='Open'
        )
        
        self.client.force_login(self.user)
        response = self.client.get('/findings/')
        # User should NOT see the secret finding (count should still be 10 on page 1, and total count 15)
        # Check total count in paginator
        self.assertEqual(response.context['page_obj'].paginator.count, 15)
        
        self.client.force_login(self.superuser)
        response = self.client.get('/findings/')
        # Superuser SHOULD see it (total count 16)
        self.assertEqual(response.context['page_obj'].paginator.count, 16)
