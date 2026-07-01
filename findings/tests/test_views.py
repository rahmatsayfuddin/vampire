from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from organizations.models import Organization
from projects.models import Project
from findings.models import Finding
from assignments.models import Assignment
from django.utils import timezone
import datetime


class FindingListViewTest(TestCase):

    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'a@t.com', 'password')
        self.user = User.objects.create_user('user', 'u@t.com', 'password')

        group = Group.objects.create(name='Pentester')
        for codename in ['view_finding', 'add_finding', 'change_finding', 'delete_finding']:
            perm = Permission.objects.get(codename=codename)
            group.permissions.add(perm)
        self.user.groups.add(group)

        self.org = Organization.objects.create(name='Test Org')
        self.project = Project.objects.create(
            project_name='Test Project',
            organization=self.org,
            status='Planned',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + datetime.timedelta(days=30)
        )

        for i in range(15):
            Finding.objects.create(
                project=self.project,
                title=f'Finding {i}',
                description='Desc',
                impact='High',
                severity='High',
                status='Open'
            )

        Assignment.objects.create(project=self.project, user=self.user, title='Tester')

    def test_pagination_superuser(self):
        self.client.force_login(self.superuser)
        response = self.client.get('/findings/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 10)

        response = self.client.get('/findings/?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_user_access(self):
        self.client.force_login(self.user)
        response = self.client.get('/findings/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_unassigned_project_access(self):
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
        self.assertEqual(response.context['page_obj'].paginator.count, 15)

        self.client.force_login(self.superuser)
        response = self.client.get('/findings/')
        self.assertEqual(response.context['page_obj'].paginator.count, 16)


class ProjectDetailViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser('admin2', 'a@b.c', 'password')
        self.org = Organization.objects.create(name='Detail Test Org')
        self.project = Project.objects.create(
            project_name='Detail Project',
            organization=self.org,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + datetime.timedelta(days=30),
            status='In Progress'
        )

    def test_project_detail_returns_200(self):
        self.client.force_login(self.user)
        response = self.client.get(f'/projects/{self.project.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detail Project')
        self.assertContains(response, 'Report History')
