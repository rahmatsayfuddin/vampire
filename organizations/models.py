from django.db import models
import os

def upload_to(instance, filename):
    return os.path.join('organization_logos', filename)

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to=upload_to, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def logo_url(self):
        return self.logo.url if self.logo else None

    def __str__(self):
        return self.name
