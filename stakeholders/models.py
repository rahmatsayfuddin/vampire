from django.db import models
from projects.models import Project

class Stakeholder(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    position = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} ({self.position})"
