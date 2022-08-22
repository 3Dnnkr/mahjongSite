from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs['placeholder'] = field.label
            
class UserCreateForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class UserUpdateForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['introduction']
        widgets = {
            'introduction':forms.Textarea(attrs={'rows':3, 'cols':15})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class']='form-control'
