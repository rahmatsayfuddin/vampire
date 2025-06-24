from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password_hash', 'email', 'full_name', 'role']
        widgets = {
            'password_hash': forms.PasswordInput(),
        }
