import os
import json
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import auth
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.views import password_reset_confirm
from django.contrib.auth.tokens import default_token_generator
from piebase.models import User, Organization
from accounts.forms import EditUserModelForm, RegisterForm, ChangePasswordForm
from project.forms import PasswordResetForm
from pietrack.settings import EMAIL_HOST_USER

# for messages in views and templates
from django.contrib import messages

# for authentication and login required
from django.contrib.auth.decorators import user_passes_test, login_required

user_login_required = user_passes_test(
    lambda user: user.is_active, login_url='/')


def active_user_required(view_func):
    decorated_view_func = login_required(
        user_login_required(view_func), login_url='/')
    return decorated_view_func


def index(request):
    if request.user.id:
        return HttpResponseRedirect(reverse('project:list_of_projects'))
    return render(request, 'login.html')


@active_user_required
def logout(request):
    auth.logout(request)
    messages.success(request, 'Successfully logged out !')
    return HttpResponseRedirect("/")


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(username=email, password=password)
        if user:
            if user.is_active:
                auth.login(request, user)
                json_data = {'error': False}
            else:
                json_data = {
                    'error': True, 'error_msg': 'User account is disabled'}
        else:
            json_data = {'error': True, 'error_msg':
                         'Authenticating user failed, wrong email or password'}
        messages.success(request, 'Successfully logged in !')
        return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        return render(request, 'login.html')


def register(request):
    register_form = RegisterForm(request.POST)
    if register_form.is_valid():
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        username = request.POST.get('username')
        organization_name = request.POST.get('organization')
        domain_name = request.POST.get('domain')
        if password == confirm_password:
            if Organization.objects.filter(name=organization_name):
                pietrack_role = 'user'
                organization_obj = Organization.objects.get(
                    name=organization_name)
            else:
                pietrack_role = 'admin'
                organization_obj = Organization.objects.create(
                    name=organization_name, slug=organization_name, domain=domain_name.lower())
            json_data = {'error': False}
            new_user = User.objects.create_user(username=username, email=email, password=password,
                                                first_name=first_name, organization=organization_obj,
                                                pietrack_role=pietrack_role)
            user = auth.authenticate(username=email, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)

        else:
            json_data = {'error': True, 'error_password': 'password mismatch'}
        messages.success(request, 'You are successfully registered !')
        return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        json_data = {'error': True, 'response': register_form.errors}
        return HttpResponse(json.dumps(json_data), content_type='application/json')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            json_data = {'error': True, 'error_msg': 'This field is required'}
        else:
            if User.objects.filter(email=email).exists():
                form = PasswordResetForm(request.POST)
                if form.is_valid():
                    opts = {
                        'use_https': request.is_secure(),
                        'from_email': EMAIL_HOST_USER,
                        'email_template_name': 'email/reset_email.html',
                        'subject_template_name': 'email/reset_subject.txt',
                        'request': request}
                    form.save(**opts)
                json_data = {'error': False}
            else:
                json_data = {
                    'error': True, 'error_msg': 'email not registered'}
        messages.success(request, 'Password recovery mail has been sent to your account !')
        return HttpResponse(json.dumps(json_data), content_type='application/json')


@active_user_required
def change_password(request):
    if request.method == 'POST':
        user = request.user
        form = ChangePasswordForm(request.POST, request=request)
        if form.is_valid():
            user.set_password(request.POST['password1'])
            user.save()
            response_data = {
                'error': False, "response": 'Your password is updated !'}

        else:
            response_data = {'error': True, 'response': form.errors}

        return HttpResponse(json.dumps(response_data))
    return render(request, 'user/change_password.html')


@active_user_required
def user_profile(request):
    if request.method == 'POST':
        user = request.user
        form = EditUserModelForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            if not request.POST.get('organization'):
                response_data = {'error': True, "response": {"organization": 'Please provide organization name'}}
                return HttpResponse(json.dumps(response_data))
            organization = Organization.objects.get(id=request.user.organization.id)
            organization.name = request.POST.get('organization')
            organization.domain = request.POST.get('domain').lower()
            organization.save()

            if 'profile_pic' in request.FILES:

                user.profile_pic = request.FILES['profile_pic']
                try:
                    os.remove(settings.MEDIA_ROOT + 'profile/' +
                              user.username + '/' + user.username + '.jpg')
                except:
                    pass

            form.save()
            response_data = {'error': False, "response": 'Successfully updated'}
            messages.success(request, 'Your profile updated successfully !')
        else:
            response_data = {'error': True, 'response': form.errors}

        return HttpResponse(json.dumps(response_data))
    return render(request, 'user/user_profile.html')


def reset_confirm(request, uidb64=None, token=None):
    return password_reset_confirm(request, template_name='email/reset_confirm.html', uidb64=uidb64, token=token,
                                  post_reset_redirect=reverse('user:login'))
