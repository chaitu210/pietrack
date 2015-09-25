import json
import urllib
from django.http.response import HttpResponse
from django.conf import settings
import boto.ses
import random
import string
from django.core.mail.message import EmailMessage


def Memail(mfrom, msubject, mbody, mto, msubscribe=''):
    conn = boto.ses.connect_to_region(
        'us-east-1',
        aws_access_key_id=settings.AM_ACCESS_KEY,
        aws_secret_access_key=settings.AM_PASS_KEY)
    conn.send_email(
        settings.DEFAULT_FROM_EMAIL, msubject, mbody, mto, format='html')


def rand_string(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for x in range(size))
