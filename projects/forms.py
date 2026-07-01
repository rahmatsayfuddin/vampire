from django import forms
from .models import Project, SlaProfile


class SlaProfileForm(forms.ModelForm):
    class Meta:
        model = SlaProfile
        fields = ['name', 'description', 'sla_critical', 'sla_high', 'sla_medium', 'sla_low', 'is_default']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'description', 'scope', 'organization', 'sla_profile', 'start_date', 'end_date', 'status']

    def __init__(self, *args, **kwargs):
        organization_id = kwargs.pop('organization_id', None)
        super().__init__(*args, **kwargs)

        if organization_id:
            self.fields['organization'].initial = organization_id
            self.fields['organization'].widget = forms.HiddenInput()

        self.fields['sla_profile'].required = False
        self.fields['sla_profile'].empty_label = '— Use default SLA —'