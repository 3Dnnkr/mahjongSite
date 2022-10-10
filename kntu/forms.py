from django import forms
from .models import Examination, Comment, Seat, Release 



class ExamForm(forms.ModelForm):
    release = forms.ChoiceField(choices=Release.choices, widget=forms.RadioSelect())
    class Meta:
        model = Examination
        fields = ['title','description','release','paifudata','seat',]


class UpdateExamForm(forms.ModelForm):
    release = forms.ChoiceField(choices=Release.choices, widget=forms.RadioSelect())
    class Meta:
        model = Examination
        fields = ['release',]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class PaifuForm(forms.Form):
    url = forms.CharField()
    seat = forms.fields.ChoiceField(
        choices = (
            (0,'東一局東家'),
            (1,'東一局南家'),
            (2,'東一局西家'),
            (3,'東一局北家')
        ),
        required = True,
        widget = forms.widgets.Select
    )