from django.conf.urls import url
from . import views
urlpatterns=[
	url(r'^create-project/$',views.create_project,name='create_project'),
	url(r'^list-of-projects/$', views.list_of_projects, name='list_of_projects'),
]
