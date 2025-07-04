from django import forms
from .models import Finding
from vkb.models import VulnerabilityKnowledgeBase

class FindingForm(forms.ModelForm):
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

    vkb = forms.ModelChoiceField(
        queryset=VulnerabilityKnowledgeBase.objects.all(),
        required=False,
        label="Use VKB (optional)",
        empty_label="Custom" 
    )
    
    save_to_vkb = forms.BooleanField(required=False, label="Save to VKB if custom")
    vkb_category = forms.ChoiceField(
    choices=CATEGORY_CHOICES,
    required=False,
    initial='Other Notable Vulnerabilities',
    label="Category"
    )

    class Meta:
        model = Finding
        fields = [
            'title', 'description', 'impact', 'recommendation',
            'affected', 'severity', 'score', 'poc', 'status'
        ]
