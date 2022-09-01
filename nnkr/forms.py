#from xml.etree.ElementTree import Comment
from django import forms
from django.contrib.auth import get_user_model

from .models import Choice, Question, Comment, Tag


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['image','title','description']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text']

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

ChoiceFormset = forms.inlineformset_factory(
    Question, Choice, fields=['text'],
    extra=2, max_num=9, can_delete=False,
)