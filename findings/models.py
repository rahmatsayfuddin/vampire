from django.db import models
from django.utils import timezone
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

    # SLA logic (hardcoded)
    def sla_days(self):
        return {
            'Critical': 7,
            'High': 14,
            'Medium': 30,
            'Low': 60,
        }.get(self.severity, 30)

    def sla_due_date(self):
        return self.created_at + timedelta(days=self.sla_days())

    def is_late(self):
        if self.status == 'Closed' and self.closed_at:
            return self.closed_at > self.sla_due_date()
        if self.status == 'Open':
            return timezone.now() > self.sla_due_date()
        return False

    def sla_delay_days(self):
        if self.status == 'Closed' and self.closed_at:
            delta = (self.closed_at - self.sla_due_date()).days
            return max(0, delta)
        elif self.status == 'Open':
            delta = (timezone.now() - self.sla_due_date()).days
            return max(0, delta)
        return 0
