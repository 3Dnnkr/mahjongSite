from django.db import models
from django.contrib.auth.models import AbstractUser

from nnkr.models import Question

class User(AbstractUser):
    introduction = models.TextField(blank=True)
    pass

class Bookmark(models.Model):
    pass