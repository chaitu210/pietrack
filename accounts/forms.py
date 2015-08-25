from piebase.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

# for images dimensions
from django.core.files.images import get_image_dimensions


class EditUserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_pic', 'username', 'email', 'first_name', 'last_name', 'biography']


        # def clean_profile_pic(self):
        #     profile_pic = self.cleaned_data['profile_pic']
        #
        #     try:
        #         w, h = get_image_dimensions(profile_pic)
        #
        #         # validate dimensions
        #         max_width = max_height = 80
        #         if w > max_width or h > max_height:
        #             raise forms.ValidationError(
        #                 'Please use an image that is %s x %s pixels or smaller.' % (max_width, max_height))
        #
        #         # validate content type
        #         main, sub = profile_pic.content_type.split('/')
        #         if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
        #             raise forms.ValidationError('Please use a JPEG, GIF or PNG image.')
        #
        #         # validate file size
        #         if len(profile_pic) > (20 * 1024):
        #             raise forms.ValidationError('Avatar file size may not exceed 20k.')
        #
        #     except AttributeError:
        #         """
        #         Handles case when we are updating the user profile
        #         and do not supply a new avatar
        #         """
        #         pass


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
