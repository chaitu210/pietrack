from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext, ugettext_lazy as _
from .tasks import celery_send_mail
from piebase.models import Project, Priority, Severity, Organization, User, TicketStatus, Role, Milestone
from django.template.defaultfilters import slugify


class CreateProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization', None)
        super(CreateProjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Project
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data['name']
        if (Project.objects.filter(name=name, organization=self.organization)):
            raise forms.ValidationError('Project with this name already exists.')
        return name


class PriorityIssueForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.project = kwargs.pop('project', None)
		super(PriorityIssueForm, self).__init__(*args, **kwargs)
	
	class Meta:
		model = Priority
		fields = ['name','color']

	def clean_name(self):
		name = self.cleaned_data['name']
		project = Project.objects.get(slug=self.project);
		if(Priority.objects.filter(name=name,project=project)):
			raise forms.ValidationError('Priority with this name already exists')
		return name

class PriorityIssueFormEdit(forms.ModelForm):

	class Meta:
		model = Priority
		fields = ['name','color']

class SeverityIssueForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.project = kwargs.pop('project', None)
		super(SeverityIssueForm, self).__init__(*args, **kwargs)
	
	class Meta:
		model = Severity
		fields = ['name','color']

	def clean_name(self):
		name = self.cleaned_data['name']
		project = Project.objects.get(slug=self.project);
		if(Severity.objects.filter(name=name,project=project)):
			raise forms.ValidationError('Severity with this name already exists')
		return name

class SeverityIssueFormEdit(forms.ModelForm):

	class Meta:
		model = Severity
		fields = ['name','color']

class TicketStatusForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.project = kwargs.pop('project', None)
		super(TicketStatusForm, self).__init__(*args, **kwargs)
	
	class Meta:
		model = TicketStatus
		fields = ['name','color']

	def clean_name(self):
		name = self.cleaned_data['name']
		slug =slugify(name)
		
		project = Project.objects.get(slug=self.project);
		if(TicketStatus.objects.filter(name=name,slug=slug,project=project)):
			raise forms.ValidationError('Status with this name already exists')
		return name

class TicketStatusFormEdit(forms.ModelForm):

	class Meta:
		model = TicketStatus
		fields = ['name','color']		

class CreateMemberForm(forms.Form):
    email = forms.EmailField()
    designation = forms.CharField()
    description = forms.Textarea()


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.

        """
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }

            celery_send_mail.delay(subject_template_name, email_template_name,
                           context, from_email, user.email,
                           html_email_template_name=html_email_template_name)

class RoleAddForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super(RoleAddForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Role
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']
        slug =slugify(name)
        project = Project.objects.get(slug=self.project);
        if(Role.objects.filter(slug=slug,project=project)):
            raise forms.ValidationError('Role with this name already exists')
        return name

class CreateMilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['name', 'estimated_start', 'estimated_finish', 'status']
