# Package imports
from django.db import models


class Role(models.Model):
    """ Model: Role """

    # Field declarations
    name = models.CharField(max_length=255, unique=True)

    # Additional field declarations
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
