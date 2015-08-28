from django.conf.urls import url
from views import *
urlpatterns = [
    url(r'^create/$',  create_project, name='create_project'),
    url(r'^list/$',  list_of_projects, name='list_of_projects'),
    url(r'^(?P<slug>[-\w]+)/$',  project_detail, name='project_detail'),
    url(r'^delete/(?P<id>[0-9]+)/$',  delete_project, name='delete_project'),

    # project settings
    url(r'^(?P<slug>[-\w]+)/settings/$',  project_details, name='project_details'),

    # team
    url(r'^(?P<slug>[-\w]+)/team/$',  project_team, name='project_team'),
    url(r'^(?P<slug>[-\w]+)/create_member/$',  create_member, name='create_member'),

    # ticket status
    url(r'^(?P<slug>[-\w]+)/settings/ticket_status/$',  ticket_status, name='ticket_status'),
    # url(r'^(?P<slug>[-\w]+)/settings/ticket_status/create/$',  ticket_status, name='ticket_status'),
    url(r'^(?P<slug>[-\w]+)/settings/ticket_status/edit/$', ticket_status_edit, name='ticket_status_edit'),
    url(r'^(?P<slug>[-\w]+)/settings/ticket_status/delete/$', ticket_status_delete, name='ticket_status_delete'),

    # priority
    url(r'^(?P<slug>[-\w]+)/settings/priorities/$', issues_priorities, name='priorities'),
    url(r'^(?P<slug>[-\w]+)/settings/priority/edit/$', issues_priorities_edit, name='issues_priorities_edit'),
    url(r'^(?P<slug>[-\w]+)/settings/priority/delete/$', issues_priorities_delete, name='issues_priorities_delete'),

    # severity
    url(r'^(?P<slug>[-\w]+)/settings/severities/$', issues_severities, name='issues_severities'),
    url(r'^(?P<slug>[-\w]+)/settings/severity/edit/$', issues_severity_edit, name='issues_severity_edit'),
    url(r'^(?P<slug>[-\w]+)/settings/severity/delete/$', issues_severity_delete, name='issues_severity_delete'),

    # member roles
    url(r'^(?P<slug>[-\w]+)/settings/member_roles/$', manage_role, name='manage_role'),
    url(r'^(?P<slug>[-\w]+)/settings/member_role/edit/$', manage_role_edit, name='manage_role_edit'),
    url(r'^(?P<slug>[-\w]+)/settings/member_role/delete/$', manage_role_delete, name='manage_role_delete'),

]
