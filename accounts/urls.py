from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^$', 'accounts.views.index', name='index'),
    url(r'^login/$', 'accounts.views.login', name='login'),
    url(r'^register/$', 'accounts.views.register', name='register'),
    url(r'^forgot_password/$', 'accounts.views.forgot_password',
        name='forgot_password'),
    url(r'^profile/$', 'accounts.views.user_profile',
        name='user_profile'),
    url(r'^change_password/$', 'accounts.views.change_password',
        name='change_password'),
    url(r'^logout/$', 'accounts.views.logout', name='logout'),
    url(r'^reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'accounts.views.reset_confirm', name='reset_confirm'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
