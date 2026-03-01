from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model for NAS authentication."""

    phone_name = models.CharField(max_length=100, blank=True)
    storage_used = models.BigIntegerField(default=0)  # bytes

    def __str__(self):
        return self.username
