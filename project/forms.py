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
from piebase.models import Project, Priority, Severity, Organization, User, TicketStatus, Role, Milestone, Requirement, \
    Comment, Timeline
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.core.exceptions import ValidationError


# def CreateTimeline(content_object, event_type, project, user):
#     Timeline.objects.create(content_object=content_object, event_type=event_type, project=project)


class CreateProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization', None)
        self.user = kwargs.pop('user', None)
        super(CreateProjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Project
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance.id:
            if Project.objects.filter(name=name, organization=self.organization).exclude(id=self.instance.id):
                raise forms.ValidationError('Project with this name already exists.')
        else:
            if Project.objects.filter(name=name, organization=self.organization):
                raise forms.ValidationError('Project with this name already exists.')
        return name

    def save(self, commit=True):
        instance = super(CreateProjectForm, self).save(commit=False)
        instance.organization = self.organization
        instance.name = self.cleaned_data['name']
        instance.slug = slugify(self.cleaned_data['name'])
        instance.description = self.cleaned_data['description']
        instance.modified_date = timezone.now()
        if commit:
            instance.save()
            # CreateTimeline(project,"created",project,self.user)
        return instance


class PriorityForm(forms.ModelForm):
    class Meta:
        model = Priority
        fields = ['name', 'color']

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super(PriorityForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name_slug = slugify(self.cleaned_data.get('name'))
        existing_slug = ""
        if self.instance:
            existing_slug = self.instance.slug
        if Priority.objects.filter(slug=name_slug, project=self.project) and name_slug != existing_slug:
            raise forms.ValidationError(
                'Priority with this name already exists')
        elif len(name_slug) == 0:
            raise forms.ValidationError("Priority name must contain a letter.")
        return self.cleaned_data.get('name')

    def save(self, commit=True):
        instance = super(PriorityForm, self).save(commit=False)
        instance.project = self.project
        instance.slug = slugify(self.cleaned_data['name'])
        instance.name = self.cleaned_data['name']
        instance.color = self.cleaned_data['color']
        if commit:
            instance.save()
        return instance


class SeverityForm(forms.ModelForm):
    class Meta:
        model = Severity
        fields = ['name', 'color']

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super(SeverityForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name_slug = slugify(self.cleaned_data.get('name'))
        existing_slug = ""
        if self.instance:
            existing_slug = self.instance.slug
        if Severity.objects.filter(slug=name_slug, project=self.project) and name_slug != existing_slug:
            raise forms.ValidationError('Severity with this name already exists')
        elif len(name_slug) == 0:
            raise forms.ValidationError("Severity name must contain a letter.")
        return self.cleaned_data.get('name')

    def save(self, commit=True):
        instance = super(SeverityForm, self).save(commit=False)
        instance.project = self.project
        instance.slug = slugify(self.cleaned_data['name'])
        instance.name = self.cleaned_data['name']
        instance.color = self.cleaned_data['color']
        if commit:
            instance.save()
        return instance


class TicketStatusForm(forms.ModelForm):
    class Meta:
        model = TicketStatus
        fields = ['name', 'color']

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super(TicketStatusForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name_slug = slugify(self.cleaned_data.get('name'))
        existing_slug = ""
        if self.instance:
            existing_slug = self.instance.slug
        if TicketStatus.objects.filter(slug=name_slug, project=self.project) and name_slug != existing_slug:
            raise forms.ValidationError(
                'Ticket Status with this name already exists')
        elif len(name_slug) == 0:
            raise forms.ValidationError(
                "Ticket Status name must contain a letter.")
        return self.cleaned_data.get('name')

    def save(self, commit=True):
        instance = super(TicketStatusForm, self).save(commit=False)
        instance.project = self.project
        instance.slug = slugify(self.cleaned_data['name'])
        instance.name = self.cleaned_data['name']
        instance.color = self.cleaned_data['color']
        instance.order = TicketStatus.objects.filter(project=self.project).count()+1
        if commit:
            instance.save()
        return instance


class CreateMemberForm(forms.Form):
    email = forms.EmailField()
    designation = forms.CharField()
    description = forms.Textarea()

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug', None)
        self.organization = kwargs.pop('organization', None)
        super(CreateMemberForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if Role.objects.filter(users__email=email, project__slug=self.slug, project__organization=self.organization):
            raise ValidationError("This user is assigned to the project.")
        # if()
        return email


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

        email_message = EmailMultiAlternatives(
            subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(
                html_email_template_name, context)
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


class RoleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super(RoleForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Role
        fields = ['name']

    def clean_name(self):
        name_slug = slugify(self.cleaned_data['name'])
        if self.instance:
            existing_slug = self.instance.slug
        if Role.objects.filter(slug=name_slug, project=self.project) and name_slug != existing_slug:
            raise forms.ValidationError('Role with this name already exists')
        elif len(name_slug) == 0:
            raise forms.ValidationError("Role name must contain a letter.")
        return self.cleaned_data['name']

    def save(self, commit=True):
        instance = super(RoleForm, self).save(commit=False)
        instance.project = self.project
        instance.name = self.cleaned_data['name']
        instance.slug = slugify(self.cleaned_data['name'])

        if commit:
            instance.save()
        return instance


class MilestoneForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(MilestoneForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Milestone
        fields = ['name', 'estimated_start',
                  'estimated_finish', 'status', 'project']

    def save(self, commit=True):
        milestone = super(MilestoneForm, self).save(commit=False)
        milestone.slug = slugify(self.cleaned_data.get('name'))
        milestone.modified_date = self.cleaned_data.get('estimated_finish')
        milestone.created_by = self.user
        if commit:
            milestone.save()
        return milestone


class RequirementForm(forms.ModelForm):
    class Meta:
        model = Requirement
        fields = ['name', 'milestone', 'description']


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.task = kwargs.pop('task', None)
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)
        super(CommentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Comment
        fields = ['comment']

    def save(self, commit=True):
        instance = super(CommentForm, self).save(commit=False)
        instance.commented_by = self.user
        instance.ticket = self.task

        if commit:
            instance.save()
        return instance
