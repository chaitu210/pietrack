from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.conf import settings
from django.template import loader
from django.template.context import Context
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.core import validators
from .helper import Memail
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.mail import send_mail
import os
import string
import random
import shutil
from pietrack.settings import MEDIA_ROOT

MILESTONE_STATUS = (
    ('planned', 'Planned'),
    ('started', 'Started'),
    ('finished', 'Finished'),
)

PIETRACK_ROLES = (
    ('PIE_Admin', 'PIE Admin'),
    ('Org_Admin', 'Organization Admin'),
    ('PIE_User', 'PIE User'),
)

TICKET_TYPE = (
    ('bug', 'bug'),
    ('enhancement', 'enhancement'),
    ('task', 'task')
)


def rand_str(number):
    return ''.join(random.sample(string.ascii_lowercase, number))


def url(self, filename):
    if self.__class__ == "Project":
        return "%s/%s/%s/%s" % (self.organization.slug, self.slug, rand_str(6), filename)
    elif self.__class__.__name__ == 'Attachment':
        return "%s/%s/%s" % (self.project.organization.slug, rand_str(6), filename)
    return "%s/%s/%s/%s" % (self.organization.slug, self.project.slug, rand_str(6), filename)


def logo(self, filename):
    return "%s/%s/%s/%s" % (self.organization.slug, self.slug, 'logo', filename)


class Organization(models.Model):
    name = models.CharField(
        max_length=250, verbose_name=_("name"), unique=True)
    slug = models.SlugField(
        max_length=250, unique=True, null=False, blank=True, verbose_name=_("slug"))
    domain = models.CharField(max_length=100, verbose_name=_("domain"), unique=True)


def profile_path(instance, filename):
    return os.path.join('profile/', str(instance.username), str(instance.username) + '.jpg')


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    email_verified = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization)
    pietrack_role = models.CharField(
        _('pietrack_role'), max_length=30, choices=PIETRACK_ROLES)
    profile_pic = models.FileField(upload_to=profile_path, null=True, blank=True)
    biography = models.CharField(_('biography'), blank=True, max_length=5000)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = UserManager()

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def send_reset_pwd_mail(self):
        uidb64 = urlsafe_base64_encode(str(self.pk))
        token = default_token_generator.make_token(self)

        t = loader.get_template('emails/resetpwd_email.html')
        c = Context({'uidb64': uidb64, 'token': token})
        rendered = t.render(c)
        Memail(settings.DEFAULT_FROM_EMAIL, "Reset your password", rendered, self.email)

    def send_activate_mail(self):
        uidb64 = urlsafe_base64_encode(str(self.pk))
        token = default_token_generator.make_token(self)

        t = loader.get_template('emails/activate_email.html')
        c = Context({'uidb64': uidb64, 'token': token})
        subject = "Activate your account"
        rendered = t.render(c)
        Memail(settings.DEFAULT_FROM_EMAIL, subject, rendered, self.email)


class Project(models.Model):
    name = models.CharField(max_length=250, verbose_name=_("name"))
    slug = models.SlugField(max_length=250, null=False, blank=True, verbose_name=_("slug"))
    description = models.TextField(verbose_name=_("description"))
    created_date = models.DateTimeField(verbose_name=_("created date"), auto_now_add=True)
    modified_date = models.DateTimeField(verbose_name=_("modified date"))
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="projects")
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="admin_projects")
    organization = models.ForeignKey(Organization)
    logo = models.FileField(upload_to=logo, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        super(Project, self).delete(*args, **kwargs)
        shutil.rmtree(MEDIA_ROOT + "%s/%s/" % (self.organization.slug, self.slug))

    class Meta:
        unique_together = [("name", "organization")]


class Attachment(models.Model):
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True)
    created_date = models.DateTimeField(verbose_name=_("created date"), auto_now_add=True)
    attached_file = models.FileField(max_length=500, null=True, blank=True, upload_to=url,
                                     verbose_name=_("attached file"))
    order = models.IntegerField(default=0, verbose_name=_("order"))
    project = models.ForeignKey(Project)

    def filename(self):
        return os.path.basename(self.attached_file.name)

    def __str__(self):
        return self.filename()

    def delete(self, *args, **kwargs):
        super(Attachment, self).delete(*args, **kwargs)
        shutil.rmtree(os.path.abspath(os.path.join(self.attached_file.path, os.pardir)))


class Role(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("name"))
    slug = models.SlugField(max_length=250, null=False, blank=True, verbose_name=_("slug"))
    project = models.ForeignKey(Project, null=True, blank=False, related_name="roles", verbose_name=_("project"))
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="user_roles")

    class Meta:
        unique_together = [("slug", "project")]

    def __str__(self):
        return self.name


class Milestone(models.Model):
    name = models.CharField(
        max_length=200, db_index=True, verbose_name=_("name"))
    # TODO: Change the unique restriction to a unique together with the
    # project id
    slug = models.SlugField(max_length=250, db_index=True, null=False, blank=True, verbose_name=_("slug"))
    project = models.ForeignKey(Project, related_name="milestones", verbose_name=_("project"))
    estimated_start = models.DateField(verbose_name=_("estimated start date"))
    estimated_finish = models.DateField(verbose_name=_("estimated finish date"))
    created_date = models.DateTimeField(verbose_name=_("created date"), auto_now_add=True)
    modified_date = models.DateTimeField(verbose_name=_("modified date"))
    status = models.CharField(max_length=200, choices=MILESTONE_STATUS, default="planned")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    class Meta:
        ordering = ["created_date"]
        unique_together = [("name", "project"), ("slug", "project")]

    def __str__(self):
        return self.name


class TicketStatus(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    slug = models.SlugField(max_length=255, null=False, blank=True, verbose_name=_("slug"))
    color = models.CharField(max_length=20, default="#999999", verbose_name=_("color"))
    project = models.ForeignKey(Project, related_name="task_statuses", verbose_name=_("project"))
    order = models.IntegerField(default=1, blank=True)
    is_final = models.BooleanField(default=False)

    class Meta:
        unique_together = (("project", "name"), ("project", "slug"))
        ordering = ['order']

    def __str__(self):
        return self.name


class Priority(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    slug = models.SlugField(max_length=255, null=False, blank=True, verbose_name=_("slug"))
    color = models.CharField(max_length=20, default="#999999", verbose_name=_("color"))
    project = models.ForeignKey(Project, related_name="priorities", verbose_name=_("project"))
    order = models.IntegerField(default=1, blank=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ['order']

    def __str__(self):
        return self.name


class Severity(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    slug = models.SlugField(max_length=255, null=False, blank=True, verbose_name=_("slug"))
    color = models.CharField(max_length=20, default="#999999", verbose_name=_("color"))
    project = models.ForeignKey(Project, related_name="severities", verbose_name=_("project"))
    order = models.IntegerField(default=1, blank=True)

    class Meta:
        unique_together = ("project", "name")
        ordering = ['order']

    def __str__(self):
        return self.name


class Ticket(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("name"))
    slug = models.SlugField(max_length=250, null=False, blank=True, verbose_name=_("slug"))
    project = models.ForeignKey(Project, related_name="project_tickets", verbose_name=_("project"))
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    milestone = models.ForeignKey(Milestone, null=True, blank=True, default=None, related_name="tasks",
                                  verbose_name=_("milestone"))
    created_date = models.DateTimeField(verbose_name=_("created date"), auto_now_add=True)
    modified_date = models.DateTimeField(verbose_name=_("modified date"), auto_now_add=True)
    finished_date = models.DateTimeField(verbose_name=_("finished date"))
    order = models.IntegerField(default=1)
    description = models.TextField(null=False, blank=True, verbose_name=_("description"))
    attachments = models.ManyToManyField(Attachment, blank=True)
    reference = models.ForeignKey('self', related_name='references', null=True, blank=True)
    status = models.ForeignKey(TicketStatus, null=True, blank=True, related_name="tickets", verbose_name=_("status"))
    severity = models.ForeignKey(Severity, null=True, blank=True, related_name="severity_tickets",
                                 verbose_name=_("severity"))
    priority = models.ForeignKey(Priority, null=True, blank=True, related_name="priority_tickets",
                                 verbose_name=_("priority"))
    ticket_type = models.CharField(blank=True, max_length=50, choices=TICKET_TYPE, default='task')
    target_date = models.DateField(null=True, blank=True, verbose_name=_("target date"))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_tickets", null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Comment(models.Model):
    comment = models.TextField(null=False)
    commented_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="comments")
    ticket = models.ForeignKey(Ticket, related_name="ticket_comments")
    attachments = models.ManyToManyField(Attachment, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name="comment_parent")

    def __str__(self):
        return self.comment


class Timeline(models.Model):
    content_type = models.ForeignKey(ContentType, related_name="content_type_timelines")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    namespace = models.CharField(max_length=250, default="default", db_index=True)
    # explination
    event_type = models.CharField(max_length=250, db_index=True)  # created,updated,commented,movedfrom(task),
    project = models.ForeignKey(Project, null=True)
    data = models.TextField(null=True, blank=True, verbose_name=_("data"))  # left as blank
    data_content_type = models.ForeignKey(ContentType, related_name="data_timelines", null=True)  # left as blank
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    is_read = models.BooleanField(default=False)

    class Meta:
        index_together = [('content_type', 'object_id', 'namespace'), ]

    def __str__(self):
        return self.namespace


class Labels(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    slug = models.SlugField(max_length=255, null=False, blank=True, verbose_name=_("slug"))
    color = models.CharField(max_length=20, default="#999999", verbose_name=_("color"))
    project = models.ForeignKey(Project, related_name="labels", verbose_name=_("project"))
    order = models.IntegerField(default=1, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class GitLab(models.Model):
    secret_key = models.CharField(max_length=255, verbose_name=_("secret_key"))
    git_id = models.CharField(max_length=100, verbose_name=_("git_id"))
    git_url = models.URLField(max_length=255, verbose_name=_("git_url"))
    project = models.ForeignKey(Project, related_name="git_lab", verbose_name=_("project"))

    def __str__(self):
        return self.project.name
