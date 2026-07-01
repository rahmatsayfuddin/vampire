from django.db import models
from organizations.models import Organization

class Project(models.Model):
    STATUS_CHOICES = [
        ('Planned', 'Planned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]

    project_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    scope = models.TextField(blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.RESTRICT)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In Progress')
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def spi(self):
        from .services import ProjectMetricsService
        return ProjectMetricsService.spi(self)

    def __str__(self):
        return self.project_name
