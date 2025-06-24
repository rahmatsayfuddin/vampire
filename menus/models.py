from django.db import models

class Menu(models.Model):
    menu_name = models.CharField(max_length=100, unique=True)
    menu_url = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.menu_name
