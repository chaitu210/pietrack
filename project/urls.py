from django.conf.urls import url
from . import views
urlpatterns=[
	url(r'^create-project/$',views.create_project, name='create_project'),
	url(r'^edit/(?P<slug>[a-zA-Z0-9-]+)$', views.project_details, name='project_details'),
	url(r'^create/$', views.create_project, name='create_project'),
	url(r'^list_of_projects/$', views.list_of_projects, name='list_of_projects'),
	url(r'^create_member/(\d*)/$', views.create_member, name='create_member'),
	url(r'^project-description/(?P<pk>[0-9]+)/$', views.project_description, name='project_description'),
	url(r'^delete/(?P<id>[0-9]+)/$', views.delete_project, name='delete_project'),
	url(r'^issues-priorities/(?P<slug>[a-zA-Z0-9-]+)/$',views.issues_priorities,name='issues_priorities'),
	url(r'^issues-priorities/edit/(?P<slug>[a-zA-Z0-9-]+)/$',views.issues_priorities_edit,name='issues_priorities_edit'),
	url(r'^issues-priorities/delete/(?P<slug>[a-zA-Z0-9-]+)/$',views.issues_priorities_delete,name='issues_priorities_delete'),
	url(r'^issues-severities/(?P<slug>[a-zA-Z0-9-]+)/$',views.issues_severities,name='issues_severities'),
	url(r'^issues-severities/edit/(?P<slug>[a-zA-Z0-9-]+)/$',views.issues_severities_edit,name='issues_severities_edit'),
	url(r'^issues-severities/delete/(?P<slug>[a-zA-Z0-9-]+)/$',views.issues_severities_delete,name='issues_severities_delete'),
	url(r'^ticket_status/(?P<slug>[a-zA-Z0-9-]+)/$',views.ticket_status,name='ticket_status'),
	url(r'^ticket_status/edit/(?P<slug>[a-zA-Z0-9-]+)/$',views.ticket_status_edit,name='ticket_status_edit'),
	url(r'^ticket_status/delete/(?P<slug>[a-zA-Z0-9-]+)/$',views.ticket_status_delete,name='ticket_status_delete'),
    url(r'reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 'project.views.reset_confirm', name='reset_confirm'),
	url(r'^members/(?P<slug>([a-zA-Z0-9-]+))/$',views.manage_members,name='manage_members'),
]
