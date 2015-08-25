import re
from django import forms
from piebase.models import User

class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget = forms.PasswordInput)
    organization = forms.CharField()
    class Meta:
        model = User
        fields = ['email', 'first_name', 'password', 'username']

class ChangePasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    old_password = forms.CharField(widget = forms.PasswordInput)
    new_password = forms.CharField(widget = forms.PasswordInput)
    confirm_password = forms.CharField(widget = forms.PasswordInput)

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if not new_password == confirm_password:
            raise forms.ValidationError('password missmatch')

    def clean_old_password(self):
        user_obj = User.objects.get(id = self.user_id)
        old_password = self.cleaned_data.get('old_password')
        if not user_obj.check_password(old_password):
            raise forms.ValidationError('wrong password')

