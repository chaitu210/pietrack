from django.conf.urls import url
from . import views
urlpatterns=[
	url(r'^create_project/$', views.create_project, name='create_project'),
	url(r'^list_of_projects/$', views.list_of_projects, name='list_of_projects'),
	url(r'^create_member/(\d*)/$', views.create_member, name='create_member'),
]
