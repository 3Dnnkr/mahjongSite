from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    introduction = models.TextField(blank=True)
    pass