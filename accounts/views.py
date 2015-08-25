from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import render, HttpResponse
from django.contrib import auth
from django.core.mail import send_mail
from accounts.forms import RegisterForm, ChangePasswordForm
from django.http import HttpResponseRedirect, HttpResponse

from piebase.models import User, Organization
from .forms import EditUserModelForm, RegisterForm, ChangePasswordForm
import json


# for renaming the profile pic
import os
from django.conf import settings


# Create your views here.

def index(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(username=email, password=password)
        if user:
            if user.is_active:
                auth.login(request, user)
                json_data = {'error': False}
            else:
                json_data = {'error': True, 'error_msg': 'User account is disabled'}
        else:
            json_data = {'error': True, 'error_msg': 'Authenticating user failed, wrong email or password'}
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
        if password == confirm_password:
            if Organization.objects.filter(name = organization_name):
                pietrack_role = 'user'
                organization_obj = Organization.objects.get(name = organization_name)
            else:
                pietrack_role = 'admin'
                organization_obj = Organization.objects.create(name = organization_name, slug = organization_name)
            json_data = {'error': False}
            new_user = User.objects.create_user(username = username, email = email, password = password, first_name = first_name, organization = organization_obj, pietrack_role = pietrack_role)
        else:
            json_data = {'error': True, 'error_password': 'password mismatch'}
        return HttpResponse(json.dumps(json_data), content_type = 'application/json')
    else:
        json_data = {'error': True, 'response': register_form.errors}
        return HttpResponse(json.dumps(json_data), content_type = 'application/json')


def forgot_password(request):
    if request.method == 'POST':
        email = str(request.POST.get('email'))
        if not email:
            json_data = {'error': True, 'error_msg': 'This field is required'}
        else:
            if User.objects.filter(email=email).exists():
                json_data = {'error': False}
                # send_mail('Subject here', 'Here is the message.', 'dineshmcmf@gmail.com', [email])
            else:
                json_data = {'error': True, 'error_msg': 'email not registered'}
        return HttpResponse(json.dumps(json_data), content_type='application/json')


def change_password(request):
    # user = User.objects.get(username=request.user.username)
    user = request.user

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, request=request)

        if form.is_valid():

            user.set_password(request.POST['password1'])
            user.save()

            response_data = {'error': False, "response": 'Your password is updated !'}
            return HttpResponse(json.dumps(response_data), content_type='application/json')
        else:
            response_data = {'error': True, 'response': form.errors}
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    return render(request, 'change_password.html')


def user_profile(request):
    user = request.user

    if request.method == 'POST':

        form = EditUserModelForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            if 'profile_pic' in request.FILES:

                user.profile_pic = request.FILES['profile_pic']
                try:
                    os.remove(settings.MEDIA_ROOT+'profile/'+user.username+'/'+user.username+'.jpg')
                except:
                    pass

            form.save()
            response_data = {'error': False, "response": 'Successfully updated'}
            return HttpResponse(json.dumps(response_data), content_type='application/json')
        else:
            response_data = {'error': True, 'response': form.errors}

            return HttpResponse(json.dumps(response_data), content_type="application/json")
    form = EditUserModelForm(instance=user)

    context = {'form': form}
    return render(request, 'user-profile.html', context)
