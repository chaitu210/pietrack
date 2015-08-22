from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns(
    'accounts.views',

    url(r'^$', 'index', name='index'),
    url(r'^register/$', 'register', name='register'),
    url(r'^forgot_password/$', 'forgot_password', name='forgot_password'),
    url(r'^userProfile/$', 'userProfile', name='userProfile'),
    url(r'^changePassword/$', 'changePassword', name='changePassword'),
    url(r'^createAccount/$', 'createAccount', name='createAccount'),
    url(r'^createProject/$', 'createProject', name='createProject'),
    url(r'^listOfProjects/$', 'listOfProjects', name='listOfProjects'),
    url(r'^projectDescription/$', 'projectDescription', name='projectDescription'),

    url(r'^testHtml/$', 'testHtml', name='testHtml'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
