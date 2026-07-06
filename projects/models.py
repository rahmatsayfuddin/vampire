from django.db import models
from organizations.models import Organization
from django.conf import settings


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


class ScanReport(models.Model):
    TOOL_CHOICES = [
        ('burp', 'Burp Suite'),
        ('zap', 'OWASP ZAP'),
        ('nessus', 'Nessus'),
        ('acunetix', 'Acunetix'),
        ('nmap', 'Nmap'),
        ('openvas', 'OpenVAS CSV'),
        ('csv', 'Generic CSV'),
    ]
    STATUS_CHOICES = [
        ('parsing', 'Parsing'),
        ('done', 'Done'),
        ('error', 'Error'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='scan_reports')
    file = models.FileField(upload_to='scans/')
    source_tool = models.CharField(max_length=20, choices=TOOL_CHOICES)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='parsing')

    def __str__(self):
        return f'{self.source_tool} — {self.file.name}'


class ScanFinding(models.Model):
    report = models.ForeignKey(ScanReport, on_delete=models.CASCADE, related_name='findings')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=20)
    affected = models.CharField(max_length=255, blank=True)
    recommendation = models.TextField(blank=True)
    promoted_to = models.ForeignKey('findings.Finding', null=True, blank=True, on_delete=models.SET_NULL)
    is_false_positive = models.BooleanField(default=False)

    def __str__(self):
        return f'[{self.severity}] {self.title}'


class ProjectNote(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user}: {self.content[:60]}'
