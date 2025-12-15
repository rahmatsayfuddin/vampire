from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from projects.models import Project
from organizations.models import Organization

class AccessControlTest(TestCase):
    def setUp(self):
        # Create roles
        from django.core.management import call_command
        call_command('setup_roles')

        # Create users
        self.manager = User.objects.create_user('manager', '[email protected]', 'password')
        self.manager.groups.add(Group.objects.get(name='Manager'))

        self.pentester = User.objects.create_user('pentester', '[email protected]', 'password')
        self.pentester.groups.add(Group.objects.get(name='Pentester'))

        self.viewer = User.objects.create_user('viewer', '[email protected]', 'password')
        self.viewer.groups.add(Group.objects.get(name='Viewer'))

        # Create dummy data
        self.organization = Organization.objects.create(name='Test Organization')
        from django.utils import timezone
        import datetime
        self.project = Project.objects.create(
            project_name='Test Project', 
            organization=self.organization, 
            status='Planned',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + datetime.timedelta(days=30)
        )

    def test_involved_only_access(self):
        from assignments.models import Assignment
        
        # Create another project
        other_project = Project.objects.create(
            project_name='Other Project', 
            organization=self.organization, 
            status='Planned',
            start_date=self.project.start_date,
            end_date=self.project.end_date
        )

        # Assign pentester to self.project ONLY
        Assignment.objects.create(project=self.project, user=self.pentester, title='Tester')

        self.client.force_login(self.pentester)
        
        # Should see self.project
        response = self.client.get('/projects/')
        self.assertContains(response, self.project.project_name)
        
        # Should NOT see other_project
        self.assertNotContains(response, other_project.project_name)

        # Should be able to access detail of self.project
        response = self.client.get(f'/projects/{self.project.pk}/')
        self.assertEqual(response.status_code, 200)

        # Should NOT be able to access detail of other_project (404 because of get_object_or_404 filter)
        response = self.client.get(f'/projects/{other_project.pk}/')
        self.assertEqual(response.status_code, 404)

    def test_dashboard_redirect(self):
        self.client.force_login(self.pentester)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200) # Should be dashboard
        self.assertTemplateUsed(response, 'dashboard.html')
