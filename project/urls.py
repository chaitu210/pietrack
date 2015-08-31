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
    url(r'^(?P<slug>[-\w]+)/settings/ticket_status/create/$',  ticket_status_create, name='ticket_status_create'),
    url(r'^(?P<slug>[-\w]+)/settings/ticket_status/(?P<ticket_slug>[a-zA-Z0-9-]+)/edit/$', ticket_status_edit, name='ticket_status_edit'),
    url(r'^(?P<slug>[-\w]+)/settings/ticket_status/(?P<ticket_slug>[a-zA-Z0-9-]+)/delete/$', ticket_status_delete, name='ticket_status_delete'),

    # priority
    url(r'^(?P<slug>[-\w]+)/settings/priorities/$', priorities, name='priorities'),
    url(r'^(?P<slug>[-\w]+)/settings/priority/create/$', priorities_create, name='priorities_create'),
    url(r'^(?P<slug>[-\w]+)/settings/priority/(?P<priority_slug>[a-zA-Z0-9-]+)/edit/$', priorities_edit, name='priorities_edit'),
    url(r'^(?P<slug>[-\w]+)/settings/priority/(?P<priority_slug>[a-zA-Z0-9-]+)/delete/$', priorities_delete, name='priorities_delete'),

    # severity
    url(r'^(?P<slug>[-\w]+)/settings/severities/$', severities, name='severities'),
    url(r'^(?P<slug>[-\w]+)/settings/severity/create/$', severities_create, name='severities_create'),
    url(r'^(?P<slug>[-\w]+)/settings/severity/(?P<severity_slug>[a-zA-Z0-9-]+)/edit/$', severity_edit, name='severity_edit'),
    url(r'^(?P<slug>[-\w]+)/settings/severity/(?P<severity_slug>[a-zA-Z0-9-]+)/delete/$', severity_delete, name='severity_delete'),

    # member roles
    url(r'^(?P<slug>[-\w]+)/settings/roles/$', manage_role, name='manage_role'),
    url(r'^(?P<slug>[-\w]+)/settings/role/create/$', manage_role_create, name='manage_role_create'),
    url(r'^(?P<slug>[-\w]+)/settings/role/(?P<member_role_slug>([a-zA-Z0-9-]+))/edit/$', manage_role_edit, name='manage_role_edit'),
    url(r'^(?P<slug>[-\w]+)/settings/role/(?P<member_role_slug>([a-zA-Z0-9-]+))/delete/$', manage_role_delete, name='manage_role_delete'),

]
