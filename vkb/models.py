from django.db import models

class VulnerabilityKnowledgeBase(models.Model):
    CATEGORY_CHOICES = [
        ('Injection-Based Vulnerabilities', 'Injection-Based Vulnerabilities'),
        ('Authentication & Session Flaws', 'Authentication & Session Flaws'),
        ('Access Control Issues', 'Access Control Issues'),
        ('Security Misconfigurations', 'Security Misconfigurations'),
        ('Data Exposure & Cryptographic Failures', 'Data Exposure & Cryptographic Failures'),
        ('Web & API-Specific Vulnerabilities', 'Web & API-Specific Vulnerabilities'),
        ('Memory & Low-Level Vulnerabilities', 'Memory & Low-Level Vulnerabilities'),
        ('Other Notable Vulnerabilities', 'Other Notable Vulnerabilities'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    impact = models.TextField()
    recommendation = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.title