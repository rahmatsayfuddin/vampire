from django.db import models
from datetime import timedelta
from projects.models import Project
from vkb.models import VulnerabilityKnowledgeBase

class Finding(models.Model):
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Risk Acceptance', 'Risk Acceptance'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    impact = models.TextField()
    recommendation = models.TextField()
    affected = models.TextField(max_length=255, default='Not specified')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='Low')
    score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    poc = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    closed_at = models.DateTimeField(null=True, blank=True)
    vkb_reference = models.ForeignKey(VulnerabilityKnowledgeBase, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def sla_days(self):
        from .services import SlaService
        return SlaService.sla_days(self)

    def sla_due_date(self):
        from .services import SlaService
        return SlaService.sla_due_date(self)

    def is_late(self):
        from .services import SlaService
        return SlaService.is_late(self)

    def sla_delay_days(self):
        from .services import SlaService
        return SlaService.sla_delay_days(self)
