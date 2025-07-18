from django.db import models
from products.models import Product
from django.utils import timezone

class Project(models.Model):
    STATUS_CHOICES = [
        ('Planned', 'Planned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]

    project_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Planned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In Progress')
    start_date = models.DateField()
    end_date = models.DateField()  # deadline
    completed_date = models.DateField(null=True, blank=True)

    def spi(self):
        if not self.end_date or not self.start_date:
            return None

        planned_duration = (self.end_date - self.start_date).days

        if planned_duration <= 0:
            return None

        if self.completed_date:
            actual_duration = (self.completed_date - self.start_date).days
        else:
            actual_duration = (timezone.now().date() - self.start_date).days

        if actual_duration <= 0:
            return None

        spi_value = planned_duration / actual_duration
        return round(spi_value, 2)



    def __str__(self):
        return self.project_name
