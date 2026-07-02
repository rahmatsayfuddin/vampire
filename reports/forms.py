from django import forms
from .models import ReportTemplate


class ReportTemplateForm(forms.ModelForm):
    class Meta:
        model = ReportTemplate
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 30, 'style': 'font-family: monospace;'}),
        }
