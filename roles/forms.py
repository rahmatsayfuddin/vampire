from django import forms
from .models import Role
from menus.models import Menu

class RoleForm(forms.ModelForm):
    menus = forms.ModelMultipleChoiceField(
        queryset=Menu.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Role
        fields = ['role_name', 'description', 'menus']
