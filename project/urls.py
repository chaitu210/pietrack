from django.conf.urls import url
from views import *
urlpatterns = [
    url(r'^create/$',  create_project, name='create_project'),
    url(r'^list/$',  list_of_projects, name='list_of_projects'),
    url(r'^(?P<slug>[-\w]+)/$',  project_detail, name='project_detail'),
    url(r'^delete/(?P<id>[0-9]+)/$',  delete_project, name='delete_project'),

    # project settings
    url(r'^(?P<slug>[-\w]+)/settings/$',  project_details, name='project_details'),
    url(r'^(?P<slug>[-\w]+)/edit/$',  project_edit, name='project_edit'),

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
    url(r'^(?P<slug>[-\w]+)/settings/priority/create/$', priority_create, name='priority_create'),
    url(r'^(?P<slug>[-\w]+)/settings/priority/(?P<priority_slug>[a-zA-Z0-9-]+)/edit/$', priority_edit, name='priority_edit'),
    url(r'^(?P<slug>[-\w]+)/settings/priority/(?P<priority_slug>[a-zA-Z0-9-]+)/delete/$', priority_delete, name='priority_delete'),

    # severity
    url(r'^(?P<slug>[-\w]+)/settings/severities/$', severities, name='severities'),
    url(r'^(?P<slug>[-\w]+)/settings/severity/create/$', severity_create, name='severity_create'),
    url(r'^(?P<slug>[-\w]+)/settings/severity/(?P<severity_slug>[a-zA-Z0-9-]+)/edit/$', severity_edit, name='severity_edit'),
    url(r'^(?P<slug>[-\w]+)/settings/severity/(?P<severity_slug>[a-zA-Z0-9-]+)/delete/$', severity_delete, name='severity_delete'),

    # member roles
    url(r'^(?P<slug>[-\w]+)/settings/member_roles/$', member_roles, name='member_roles'),
    url(r'^(?P<slug>[-\w]+)/settings/member_role/create/$', member_role_create, name='member_role_create'),
    url(r'^(?P<slug>[-\w]+)/settings/member_role/(?P<member_role_slug>([a-zA-Z0-9-]+))/edit/$', member_role_edit, name='member_role_edit'),
    url(r'^(?P<slug>[-\w]+)/settings/member_role/(?P<member_role_slug>([a-zA-Z0-9-]+))/delete/$', member_role_delete, name='member_role_delete'),

    # taskboard
    url(r'^(?P<slug>[-\w]+)/(?P<milestone_slug>[-\w]+)/taskboard/$', taskboard, name="taskboard"),
    url(r'^(?P<slug>[-\w]+)/update_taskboard/(?P<status_slug>([a-zA-Z0-9-]+))/(?P<task_id>[0-9]+)/$', update_taskboard_status,name="update_taskboard_status"),
    url(r'^(?P<slug>[-\w]+)/(?P<milestone_slug>[-\w]+)/(?P<status_slug>[-\w]+)/load_tasks/$', load_tasks, name="load_tasks"),
    url(r'^(?P<slug>[-\w]+)/(?P<milestone_slug>[-\w]+)/(?P<requirement_id>[0-9]+)/$',requirement_tasks, name="requirement_tasks"),
    url(r'^(?P<slug>[-\w]+)/(?P<milestone_slug>[-\w]+)/(?P<status_slug>[-\w]+)/(?P<requirement_id>[0-9]+)/load_tasks/$', requirement_tasks_more, name="requirement_tasks_more"),    
    url(r'^(?P<slug>[-\w]+)/(?P<milestone_slug>[-\w]+)/task/(?P<task_id>[0-9]+)/$',task_details, name="task_details"),

    #comments 
    url(r'^(?P<slug>[-\w]+)/task/(?P<task_id>[0-9]+)/comment/$',task_comment, name="task_comment"),


    #milestone
    url(r'^(?P<slug>[a-zA-Z0-9-]+)/milestone/create/$',milestone_create, name='milestone_create'),
    url(r'^(?P<slug>[a-zA-Z0-9-]+)/milestone/edit/$',milestone_edit, name='milestone_edit'),
    url(r'^(?P<slug>[a-zA-Z0-9-]+)/milestone/delete/$',milestone_delete, name='milestone_delete'),

    #requirement
    url(r'^(?P<slug>[a-zA-Z0-9-]+)/requirement/create/$',requirement_create, name='requirement_create'),
]

