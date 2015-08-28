from django.conf.urls import url
from views import *
urlpatterns = [
    url(r'^create/$',  create_project, name='create_project'),
    url(r'^list/$',  list_of_projects, name='list_of_projects'),
    url(r'^(?P<slug>[-\w]+)/$',  project_detail, name='project_detail'),
    url(r'^(?P<slug>[-\w]+)/settings/$',  project_details, name='project_details'),
    url(r'^(?P<slug>[-\w]+)/team/$',  project_team, name='project_team'),
    url(r'^(?P<slug>[-\w]+)/create_member/$',  create_member, name='create_member'),

    url(r'^(?P<slug>[-\w]+)/settings/ticket_status/$',  ticket_status, name='ticket_status'),

    url(r'^delete/(?P<id>[0-9]+)/$',  delete_project, name='delete_project'),
    url(r'^issues-priorities/(?P<slug>[a-zA-Z0-9-]+)/$', issues_priorities, name='issues_priorities'),
    url(r'^issues-priorities/edit/(?P<slug>[a-zA-Z0-9-]+)/$', issues_priorities_edit, name='issues_priorities_edit'),
    url(r'^issues-priorities/delete/(?P<slug>[a-zA-Z0-9-]+)/$', issues_priorities_delete, name='issues_priorities_delete'),
    url(r'^issues-severities/(?P<slug>[a-zA-Z0-9-]+)/$', issues_severities, name='issues_severities'),
    url(r'^issues-severities/edit/(?P<slug>[a-zA-Z0-9-]+)/$', issues_severities_edit, name='issues_severities_edit'),
    url(r'^issues-severities/delete/(?P<slug>[a-zA-Z0-9-]+)/$', issues_severities_delete, name='issues_severities_delete'),
    # url(r'^ticket_status/(?P<slug>[a-zA-Z0-9-]+)/$', ticket_status, name='ticket_status'),
    url(r'^ticket_status/edit/(?P<slug>[a-zA-Z0-9-]+)/$', ticket_status_edit, name='ticket_status_edit'),
    url(r'^ticket_status/delete/(?P<slug>[a-zA-Z0-9-]+)/$', ticket_status_delete, name='ticket_status_delete'),
    url(r'reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 'project.views.reset_confirm', name='reset_confirm'),
    url(r'^role/(?P<slug>([a-zA-Z0-9-]+))/$', manage_role, name='manage_role'),
    url(r'^role/edit/(?P<slug>([a-zA-Z0-9-]+))/$', manage_role_edit, name='manage_role_edit'),
    url(r'^role/delete/(?P<slug>([a-zA-Z0-9-]+))/$', manage_role_delete, name='manage_role_delete'),

]
