from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'description', 'product', 'start_date', 'end_date', 'status']

    def __init__(self, *args, **kwargs):
        product_id = kwargs.pop('product_id', None)
        super().__init__(*args, **kwargs)

        if product_id:
            self.fields['product'].initial = product_id
            self.fields['product'].widget = forms.HiddenInput()