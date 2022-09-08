from django import forms
from django.contrib.auth import get_user_model

from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title','content',]
