from django.db import models


# Create your models here.
class JobRole(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    embedding_vector = models.JSONField()

    # Additional fields
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

