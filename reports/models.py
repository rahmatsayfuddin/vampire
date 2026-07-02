from django.db import models
from django.utils import timezone
from projects.models import Project


class ReportTemplate(models.Model):
    name = models.CharField(max_length=100, default='Default')
    content = models.TextField()

    class Meta:
        verbose_name = 'Report Template'

    def __str__(self):
        return self.name


class ReportHistory(models.Model):
    FORMAT_CHOICES = [
        ('md', 'Markdown'),
    ]
    STATUS_CHOICES = [
        ('loading', 'Loading'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    file_name = models.CharField(max_length=255)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='loading')
    created_at = models.DateTimeField(auto_now_add=True)

    def file_path(self):
        return f"reports/{self.file_name}"
