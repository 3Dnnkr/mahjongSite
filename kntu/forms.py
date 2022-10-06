from django import forms

class PaifuForm(forms.Form):
    url = forms.CharField()
    seat = forms.fields.ChoiceField(
        choices = (
            (0,'東家'),
            (1,'南家'),
            (2,'西家'),
            (3,'北家')
        ),
        required = True,
        widget = forms.widgets.Select
    )