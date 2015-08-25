from django.conf.urls import url
from . import views
urlpatterns=[
	url(r'^create-project/$',views.create_project, name='create_project'),
	url(r'^list-of-projects/$', views.list_of_projects, name='list_of_projects'),
	url(r'^edit/(?P<slug>[a-zA-Z0-9-]+)$', views.project_details, name='project_details'),
	url(r'^project-description/(?P<pk>[0-9]+)/$', views.project_description, name='project_description'),
	url(r'^delete/(?P<id>[0-9]+)/$', views.delete_project, name='delete_project'),
	url(r'^issues-priorities/(?P<slug>[a-zA-Z0-9-]+)/$',views.issues_priorities,name='issues_priorities'),
	url(r'^issues-priorities/edit/(?P<slug>[a-zA-Z0-9-]+)/$',views.issues_priorities_edit,name='issues_priorities_edit'),
	url(r'^issues-priorities/delete/(?P<slug>[a-zA-Z0-9-]+)/$',views.issues_priorities_delete,name='issues_priorities_delete'),
]
