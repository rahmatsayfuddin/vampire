from django.db import models
from menus.models import Menu

class Role(models.Model):
    role_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    menus = models.ManyToManyField(Menu, through='RoleMenuAccess')

    def __str__(self):
        return self.role_name

class RoleMenuAccess(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('role', 'menu')
