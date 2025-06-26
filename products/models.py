from django.db import models
import os

def upload_to(instance, filename):
    return os.path.join('product_logos', filename)

class Product(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    product_logo = models.ImageField(upload_to=upload_to, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def product_logo_url(self):
        return self.product_logo.url if self.product_logo else None

    def __str__(self):
        return self.product_name
