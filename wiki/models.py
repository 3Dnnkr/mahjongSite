from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField
from mdeditor.fields import MDTextField



class Article(models.Model):
    title = models.CharField(max_length=100)
    content = MDTextField()