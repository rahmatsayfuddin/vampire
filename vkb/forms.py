from django import forms
from .models import VulnerabilityKnowledgeBase

class VKBForm(forms.ModelForm):
    class Meta:
        model = VulnerabilityKnowledgeBase
        fields = ['category', 'title', 'description', 'impact', 'recommendation']
