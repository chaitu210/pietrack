from celery import task
from django.core.mail import send_mail
from django.template import loader
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives, send_mail


@task()
def add():
    return 2 + 2


@task()
def send_mail_old_user(subject, message, from_email, to_email):
    send_mail(subject, message, from_email, [to_email])


@task()
def celery_send_mail(subject_template_name, email_template_name,
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
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')
    email_message.send()
