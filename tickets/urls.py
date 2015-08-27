from django.conf.urls import patterns, url

urlpatterns = [
    url(r'^add_task/$', 'tickets.views.add_task', name = 'add_task'),
]
