from django.shortcuts import render
from django.contrib.auth import *
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth

from piebase.models import User
from .forms import EditUserModelForm, RegisterForm, ChangePasswordForm
import json


# for renaming the profile pic
import os
from django.conf import settings


# Create your views here.

# for base html
def testHtml(request):
    user = User.objects.get(username=request.user)
    context = {'user': user}
    return render(request, 'base.html', context)


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
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            first_name = request.POST.get('first_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            username = request.POST.get('username')
            if password == confirm_password:
                json_data = {'error': False}
                new_user = User.objects.create_user(username=username, email=email, password=password,
                                                    first_name=first_name)

            else:
                json_data = {'error': True, 'error_password': 'password mismatch'}
            return HttpResponse(json.dumps(json_data), content_type='application/json')
        else:
            json_data = {'error': True, 'form_errors': register_form.errors}
            return HttpResponse(json.dumps(json_data), content_type='application/json')
    return render(request, 'create_account.html')


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


def createAccount(request):
    return render(request, 'create_account.html')


def createProject(request):
    return render(request, 'create_project.html')

# main change password code with views and forms validation  of new passwords matching
# def changePassword(request):
#     # user = User.objects.get(username=request.user.username)
#     user = request.user
#
#     if request.method == 'POST':
#         form = ChangePasswordForm(request.POST)
#         if form.is_valid():
#             success = user.check_password(request.POST['password'])
#
#             if success:
#                 user.set_password(request.POST['password1'])
#                 user.save()
#                 response_data = {'status': False, "passwd_change": 'Your password is updated !'}
#                 return HttpResponse(json.dumps(response_data), content_type='application/json')
#             else:
#                 response_data = {'status': True, 'passwd_change': 'Your password is incorrect'}
#                 return HttpResponse(json.dumps(response_data), content_type='application/json')
#         else:
#             response_data = {'error': True, 'errors': form.errors}
#             return HttpResponse(json.dumps(response_data), content_type="application/json")
#
#     form = ChangePasswordForm()
#     context = {'form': form, 'user': user}
#
#     return render(request, 'change_password.html', context)
#

def changePassword(request):
    # user = User.objects.get(username=request.user.username)
    user = request.user

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, request=request)

        if form.is_valid():

            user.set_password(request.POST['password1'])
            user.save()

            response_data = {'error': False, "errors": 'Your password is updated !'}
            return HttpResponse(json.dumps(response_data), content_type='application/json')
        else:
            print form.errors
            response_data = {'error': True, 'errors': form.errors}
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    form = ChangePasswordForm()
    context = {'form': form, 'user': user}

    return render(request, 'change_password.html', context)
#



def listOfProjects(request):
    return render(request, 'list_of_projects.html')


def projectDescription(request):
    return render(request, 'project_description.html')


def userProfile(request):
    user = request.user

    if request.method == 'POST':
        user = request.user
        form = EditUserModelForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            if 'profile_pic' in request.FILES:

                user.profile_pic = request.FILES['profile_pic']
                try:
                    print settings.MEDIA_ROOT+'profile/'+user.username+'/'+user.username+'.jpg'
                    os.remove(settings.MEDIA_ROOT+'profile/'+user.username+'/'+user.username+'.jpg')
                except:
                    pass

            form.save()
            response_data = {'error': False, "errors": 'Successfully updated'}
            return HttpResponse(json.dumps(response_data), content_type='application/json')
        else:
            response_data = {'error': True, 'errors': form.errors}

            return HttpResponse(json.dumps(response_data), content_type="application/json")
    form = EditUserModelForm(instance=user)

    context = {'form': form}
    return render(request, 'user-profile.html', context)
