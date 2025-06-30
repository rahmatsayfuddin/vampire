from django.db import models
from projects.models import Project
from users.models import User 

class Assignment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    class Meta:
        unique_together = ('project', 'user')  
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.full_name} - {self.title}"
