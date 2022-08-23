from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    introduction = models.TextField('紹介文',blank=True)
    bookmarks = models.ManyToManyField('nnkr.Question', through='nnkr.Bookmark', blank=True, verbose_name='ブックマーク')
    pass
