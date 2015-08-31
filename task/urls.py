from django.conf.urls import patterns, url

urlpatterns = [
    url(r'^add/$', 'task.views.add_task', name = 'add_task'),
]
