from django.db import models
from organizations.models import Organization


class SlaProfile(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    sla_critical = models.IntegerField(default=7)
    sla_high = models.IntegerField(default=14)
    sla_medium = models.IntegerField(default=30)
    sla_low = models.IntegerField(default=60)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', 'name']

    def save(self, *args, **kwargs):
        if self.is_default:
            SlaProfile.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


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
    sla_profile = models.ForeignKey(SlaProfile, null=True, blank=True, on_delete=models.SET_NULL)
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
