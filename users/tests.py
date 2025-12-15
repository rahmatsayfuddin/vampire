from django.test import TestCase, Client
from django.contrib.auth.models import User, Group

class UserManagementTest(TestCase):
    def setUp(self):
        # Create groups
        self.manager_group = Group.objects.create(name='Manager')
        self.pentester_group = Group.objects.create(name='Pentester')

        # Create users
        self.superuser = User.objects.create_superuser('admin', '[email protected]', 'password')
        
        self.manager = User.objects.create_user('manager', '[email protected]', 'password')
        self.manager.groups.add(self.manager_group)
        
        self.pentester = User.objects.create_user('pentester', '[email protected]', 'password')
        self.pentester.groups.add(self.pentester_group)

    def test_access_control(self):
        # Superuser can access
        self.client.force_login(self.superuser)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)

        # Manager can access
        self.client.force_login(self.manager)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)

        # Pentester CANNOT access
        self.client.force_login(self.pentester)
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 302) # Redirects to login (login_required + user_passes_test)

    def test_create_user(self):
        self.client.force_login(self.manager)
        response = self.client.post('/users/create/', {
            'username': 'newuser',
            'password': 'newpassword',
            'groups': [self.pentester_group.id]
        })
        self.assertEqual(response.status_code, 302) # Redirects to list
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertTrue(new_user.groups.filter(name='Pentester').exists())

    def test_create_group(self):
        self.client.force_login(self.manager)
        response = self.client.post('/roles/create/', {
            'name': 'NewRole'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Group.objects.filter(name='NewRole').exists())
