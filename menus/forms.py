from django import forms
from .models import Menu

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['menu_name', 'menu_url']
