from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^$', 'accounts.views.index', name='index'),
    url(r'login/$', 'accounts.views.login', name='login'),
    url(r'^register/$', 'accounts.views.register', name='register'),
    url(r'^forgot_password/$', 'accounts.views.forgot_password', name='forgot_password'),
    url(r'^userProfile/$', 'accounts.views.userProfile', name='userProfile'),
    url(r'^changePassword/$', 'accounts.views.changePassword', name='changePassword'),

    url(r'^testHtml/$', 'accounts.views.testHtml', name='testHtml'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
