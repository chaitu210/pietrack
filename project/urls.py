from django.conf.urls import url
from . import views

urlpatterns=[
	url(r'^create_project/$', views.create_project, name='create_project'),
	url(r'^list_of_projects/$', views.list_of_projects, name='list_of_projects'),
	url(r'^create_member/(\d*)/$', views.create_member, name='create_member'),
	url(r'^project-description/(?P<pk>[0-9]+)/$', views.project_description, name='project_description'),
     url(r'reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 'project.views.reset_confirm', name='reset_confirm'),
]
