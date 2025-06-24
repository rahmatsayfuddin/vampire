# Create your models here.
from django.db import models
from roles.models import Role

class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    role = models.ForeignKey(Role, on_delete=models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
