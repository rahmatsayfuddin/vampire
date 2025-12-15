from django import forms
from django.core.exceptions import ValidationError
from .models import Assignment
from django.contrib.auth.models import User

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['user', 'title']

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if self.project:
            # Filter users who are NOT already assigned to this project
            assigned_users = Assignment.objects.filter(project=self.project).values_list('user', flat=True)
            self.fields['user'].queryset = User.objects.exclude(id__in=assigned_users)

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        if self.project and user:
            if Assignment.objects.filter(project=self.project, user=user).exists():
                raise ValidationError(f"User {user.username} is already assigned to this project.")
        return cleaned_data
