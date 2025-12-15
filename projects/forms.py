from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'description','scope', 'organization', 'start_date', 'end_date', 'status']

    def __init__(self, *args, **kwargs):
        organization_id = kwargs.pop('organization_id', None)
        super().__init__(*args, **kwargs)

        if organization_id:
            self.fields['organization'].initial = organization_id
            self.fields['organization'].widget = forms.HiddenInput()