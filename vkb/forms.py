from django import forms
from .models import VulnerabilityKnowledgeBase

class VKBForm(forms.ModelForm):
    class Meta:
        model = VulnerabilityKnowledgeBase
        fields = ['category', 'title', 'description', 'impact', 'recommendation']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'impact': forms.Textarea(attrs={'rows': 3}),
            'recommendation': forms.Textarea(attrs={'rows': 3}),
        }
