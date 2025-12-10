from django.db import models
from django.conf import settings
from projects.models import Project

class Assignment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    class Meta:
        unique_together = ('project', 'user')  
        ordering = ['user__username']

    def __str__(self):
        name = getattr(self.user, "get_full_name", lambda: "")()
        return f"{name or self.user.username} - {self.title}"
