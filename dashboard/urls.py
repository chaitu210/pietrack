from django.conf.urls import patterns, url

urlpatterns = [
    url(r'^profile_activity$', 'dashboard.views.profile_activity',
        name='profile_activity'),
]
