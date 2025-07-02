from django.db import models

class VKBCategory(models.Model):
    code = models.CharField(max_length=1, unique=True)  # A, B, C, etc.
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code}. {self.name}"

class VulnerabilityKnowledgeBase(models.Model):
    category = models.ForeignKey(VKBCategory, on_delete=models.PROTECT)
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    impact = models.TextField()
    recommendation = models.TextField()

    def __str__(self):
        return self.title
