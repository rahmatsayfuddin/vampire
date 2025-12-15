from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from projects.models import Project
from findings.models import Finding
from vkb.models import VulnerabilityKnowledgeBase

class Command(BaseCommand):
    help = 'Setup default roles and permissions'

    def handle(self, *args, **options):
        # Define roles
        roles = {
            'Manager': {
                'models': [Project, Finding, VulnerabilityKnowledgeBase],
                'permissions': ['add', 'change', 'delete', 'view']
            },
            'Pentester': {
                'models': [Project],
                'permissions': ['view'],
                'extra_models': {
                    Finding: ['add', 'change', 'view'],
                    VulnerabilityKnowledgeBase: ['add', 'view']
                }
            },
            'Viewer': {
                'models': [Project, Finding, VulnerabilityKnowledgeBase],
                'permissions': ['view']
            }
        }

        for role_name, config in roles.items():
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(f'Created group: {role_name}')
            else:
                self.stdout.write(f'Updated group: {role_name}')
            
            # Clear existing permissions
            group.permissions.clear()

            # Add permissions for main models list
            if 'models' in config:
                for model in config['models']:
                    content_type = ContentType.objects.get_for_model(model)
                    for perm_code in config['permissions']:
                        codename = f'{perm_code}_{model._meta.model_name}'
                        try:
                            permission = Permission.objects.get(content_type=content_type, codename=codename)
                            group.permissions.add(permission)
                            self.stdout.write(f'  + Added {codename} to {role_name}')
                        except Permission.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f'  ! Permission {codename} not found'))

            # Add permissions for extra models
            if 'extra_models' in config:
                for model, perms in config['extra_models'].items():
                    content_type = ContentType.objects.get_for_model(model)
                    for perm_code in perms:
                        codename = f'{perm_code}_{model._meta.model_name}'
                        try:
                            permission = Permission.objects.get(content_type=content_type, codename=codename)
                            group.permissions.add(permission)
                            self.stdout.write(f'  + Added {codename} to {role_name}')
                        except Permission.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f'  ! Permission {codename} not found'))

        self.stdout.write(self.style.SUCCESS('Successfully setup roles and permissions'))
