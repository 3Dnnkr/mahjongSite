from django import forms
from django.contrib.auth import get_user_model

from .models import Choice, Question, Comment, Tag, Lobbychat


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['image','title','description','no_vote']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class LobbychatForm(forms.ModelForm):
    class Meta:
        model = Lobbychat
        fields = ['text']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text']

class TagForm(forms.Form):
    # Tag is unique so can't use ModelForm
    name = forms.CharField()

class PaifuForm(forms.Form):
    url = forms.CharField()

ChoiceFormset = forms.inlineformset_factory(
    Question, Choice, fields=['text'],
    extra=2, max_num=9, can_delete=False,
)