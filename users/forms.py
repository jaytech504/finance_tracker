from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
  
    class Meta:
  	    model = User
  	    fields = ['username', 'email', 'password1', 'password2']

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs)
          self.helper = FormHelper()
          self.helper.form_method = 'post'
          self.helper.add_input(Submit('submit', 'Login', css_class='btn-primary'))