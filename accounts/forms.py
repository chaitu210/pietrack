from piebase.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.files.images import get_image_dimensions

class EditUserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_pic', 'username', 'email', 'first_name', 'last_name', 'biography']

class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    organization = forms.CharField()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'password', 'username']
