from django.conf.urls import include, url

urlpatterns = [
    url(r'login/$', 'accounts.views.login', name = 'login'),
    url(r'register/$', 'accounts.views.register', name = 'register'),
    url(r'forgot_password/$', 'accounts.views.forgot_password', name = 'forgot_password'),
    url(r'reset/$', 'accounts.views.reset', name = 'reset'),
]
