from piebase.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

# for images dimensions
from django.core.files.images import get_image_dimensions


class EditUserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_pic', 'username', 'email', 'first_name', 'last_name', 'biography']


class ChangePasswordForm(forms.Form):
    password = forms.CharField(label=_("Old Password"), widget=forms.PasswordInput)
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_password(self):                                                                                                                                                                                                                                                                                                                                                                                                                                       
        auser = self.request.user
        opassword = self.request.POST['password']
        success = auser.check_password(opassword)

        if not success:
            raise forms.ValidationError(_('Old password is not matching !'))

        return opassword

    def clean_password2(self):
        form_cleaned_data = self.cleaned_data
        if 'password1' in form_cleaned_data:
            if form_cleaned_data['password1'] != form_cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."))
        return form_cleaned_data['password2']


class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    organization = forms.CharField()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'password', 'username']
