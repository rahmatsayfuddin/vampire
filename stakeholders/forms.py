from django import forms
from .models import Stakeholder

class StakeholderForm(forms.ModelForm):
    class Meta:
        model = Stakeholder
        fields = ['name', 'email', 'position']

