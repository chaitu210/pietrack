import json
import random
import string
import shutil
import os
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from piebase.models import User, Project, Priority, Severity, TicketStatus, Ticket, Requirement, Attachment, Role, \
    Milestone, Timeline, Comment
from forms import CreateProjectForm, PriorityForm, SeverityForm, TicketStatusForm, RoleForm, CommentForm, \
    CreateMemberForm, PasswordResetForm, MilestoneForm, RequirementForm
from PIL import Image
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from .tasks import send_mail_old_user
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .signals import create_timeline
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.template import *
from task.forms import TaskForm
from .templatetags.project_tags import is_project_admin
from django.utils.functional import wraps
from django.db.models import Q

def check_project_admin(view):
    wraps(view)

    def inner(request, slug, *args, **kwargs):
        try:

            role = Role.objects.get(users=request.user, project__slug=slug,
                                    project__organization=request.user.organization)

            if role.is_project_admin:
                return wraps(view) (view(request, slug, *args, **kwargs))
            elif request.user.pietrack_role == 'admin':
                return wraps(view) (view(request, slug, *args, **kwargs))
        except:
            if request.user.pietrack_role == 'admin':
                return wraps(view)(view(request, slug, *args, **kwargs))
        return HttpResponseForbidden()

    return wraps(view)(inner)


def check_organization_admin(view):
    def inner(request, *args, **kwargs):
        if request.user.pietrack_role == 'admin':
            return view(request, *args, **kwargs)
        return HttpResponseForbidden()

    return inner


user_login_required = user_passes_test(
    lambda user: user.is_active, login_url='/')


def get_notification_list(user):
    notification_list = Timeline.objects.filter(object_id=user.id)
    count = notification_list.filter(is_read=False).exclude(user=user).count()
    return (notification_list, count)


def active_user_required(view_func):
    decorated_view_func = login_required(
        user_login_required(view_func), login_url='/')
    return decorated_view_func

def is_project_member(view):
    def inner(request,slug, *args, **kwargs):
        try:
            project = Project.objects.get(slug=slug, organization=request.user.organization)
            if project.members.filter(email=request.user.email):
                return view(request,slug, *args, **kwargs)
        except:
            pass
        return HttpResponseForbidden()
    return inner

@active_user_required
@check_organization_admin
def create_project(request):
    if request.method == "POST":
        img = False
        if request.FILES.get('logo', False):
            img = True
            try:
                Image.open(request.FILES.get('logo'))
                img = False
            except:
                pass
        organization = request.user.organization
        form = CreateProjectForm(
            request.POST, organization=organization, user=request.user)
        if form.is_valid() and not img:
            slug = slugify(request.POST['name'])

            project_obj = form.save(commit=False)
            if request.FILES.get('logo', False):
                project_obj.logo = request.FILES.get('logo')

            project_obj.created_by = request.user
            project_obj.save()
            project_obj.members.add(request.user)
            project_obj.save()
            json_data = {'error': False, 'errors': form.errors, 'slug': slug}
            messages.success(request, 'Successfully created your project - ' + str(request.POST['name']) + ' !')
            return HttpResponse(json.dumps(json_data), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors, 'logo': img}),
                                content_type="application/json")
    return render(request, 'project/create_project.html')


@active_user_required
def list_of_projects(request):
    template_name = 'project/projects_list.html'
    projects_list = Project.objects.filter(members__email=request.user.email, organization=request.user.organization)
    dict_items = {'projects_list': projects_list, 'notification_list': get_notification_list(request.user)}
    return render(request, template_name, dict_items)


@active_user_required
@is_project_member
def project_detail(request, slug):
    template_name = 'project/project_description.html'
    project_object = Project.objects.get(slug=slug, organization=request.user.organization)
    events_list = project_object.timeline_set.all().order_by('-created')
    project_members = project_object.members.all()
    dict_items = {'project_object': project_object,
                  'project_members': project_members,
                  'slug': slug, 'events_list': events_list,
                  'notification_list': get_notification_list(request.user)
                  }
    return render(request, template_name, dict_items)


@active_user_required
@check_project_admin
def project_details(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    dictionary = {'project': project, 'slug': slug, 'notification_list': get_notification_list(request.user)}
    template_name = 'project/project_project_details.html'
    if request.method == 'POST':
        img = False
        if (request.FILES.get('logo', False)):
            img = True
            try:
                Image.open(request.FILES.get('logo'))
                img = False
            except:
                pass
        organization = request.user.organization
        form = CreateProjectForm(request.POST, organization=organization, instance=project)

        if form.is_valid() and not img:
            slug = slugify(request.POST['name'])
            project = Project.objects.get(
                slug=request.POST['oldname'], organization=organization)
            project.name = request.POST['name']
            project.slug = slug
            project.description = request.POST['description']
            project.modified_date = timezone.now()
            if (request.FILES.get('logo', False)):
                if (project.logo):
                    os.remove(project.logo.path)
                project.logo = request.FILES.get('logo')
            project.save()
            messages.success(request, 'Successfully updated your project - ' + str(project.name) + '')
            return HttpResponse(json.dumps({'error': False, 'slug': slug}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors, 'logo': img}),
                                content_type="application/json")

    return render(request, template_name, dictionary)


@active_user_required
@check_project_admin
def delete_project(request, slug, id):
    try:
        project = Project.objects.get(id=id, organization=request.user.organization)
        timeline_list = [project]
        milestone_list = project.milestones.all()
        timeline_list.extend(milestone_list)
        for milestone in milestone_list:
            requirement_list = milestone.requirements.all()
            timeline_list.extend(requirement_list)
            for requirement in requirement_list:
                task_list = requirement.tasks.all()
                timeline_list.extend(task_list)
                for task in task_list:
                    timeline_list.extend(task.ticket_comments.all())
        for timeline in timeline_list:
            content_type = ContentType.objects.get_for_model(timeline)
            Timeline.objects.filter(content_type__pk=content_type.id, object_id=timeline.id).delete()
        project.delete()
    except OSError as e:
        pass
    messages.success(request, 'Successfully deleted Project - ' + str(project) + ' !')
    return redirect("project:list_of_projects")


@active_user_required
@check_project_admin
def priorities(request, slug):
    priority_list = Priority.objects.filter(
        project=Project.objects.get(slug=slug, organization=request.user.organization)).order_by('id')
    return render(request, 'settings/priorities.html', {'slug': slug, 'priority_list': priority_list,
                                                        'notification_list': get_notification_list(request.user)})


@active_user_required
@check_project_admin
def priority_default(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    Priority.objects.bulk_create([Priority(name='Wishlist', slug=slugify('Wishlist'), color='#999999', project=project),
                                  Priority(name='Minor', slug=slugify('Minor'), color='#729fcf', project=project),
                                  Priority(name='Normal', slug=slugify('Normal'), color='#4e9a06', project=project),
                                  Priority(name='Important', slug=slugify('Important'), color='#f57900',
                                           project=project),
                                  Priority(name='Critical', slug=slugify('Critical'), color='#CC0000',
                                           project=project)])
    messages.success(request, 'Default priorities are added to the Priority page !')
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@active_user_required
@check_project_admin
def priority_create(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    form = PriorityForm(request.POST, project=project)
    if (form.is_valid()):
        priority = form.save()
        return HttpResponse(json.dumps(
            {'error': False, 'color': priority.color, 'name': priority.name, 'proj_id': priority.id,
             'slug': priority.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
@check_project_admin
def priority_edit(request, slug, priority_slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    instance = Priority.objects.get(slug=priority_slug, project=project)
    form = PriorityForm(request.POST, instance=instance, project=project)
    if (form.is_valid()):
        priority = form.save()
        return HttpResponse(json.dumps(
            {'error': False, 'color': priority.color, 'name': priority.name, 'proj_id': priority.id,
             'slug': priority.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
@check_project_admin
def priority_delete(request, slug, priority_slug):
    Priority.objects.get(
        slug=priority_slug, project=Project.objects.get(slug=slug, organization=request.user.organization)).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@active_user_required
@check_project_admin
def severities(request, slug):
    severity_list = Severity.objects.filter(
        project=Project.objects.get(slug=slug, organization=request.user.organization)).order_by('id')
    return render(request, 'settings/severities.html', {'slug': slug, 'severity_list': severity_list,
                                                        'notification_list': get_notification_list(request.user)})


@active_user_required
@check_project_admin
def severity_default(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    Severity.objects.bulk_create([Severity(name='Low', slug=slugify('Low'), color='#999999', project=project),
                                  Severity(name='Normal', slug=slugify('Normal'), color='#4e9a06', project=project),
                                  Severity(name='High', slug=slugify('High'), color='#cc0000', project=project)])
    messages.success(request, 'Default severities are added to the Severity page !')
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@active_user_required
@check_project_admin
def severity_create(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    form = SeverityForm(request.POST, project=project)
    if (form.is_valid()):
        severity = form.save()
        return HttpResponse(json.dumps(
            {'error': False, 'color': severity.color, 'name': severity.name, 'proj_id': severity.id,
             'slug': severity.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
@check_project_admin
def severity_edit(request, slug, severity_slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    instance = Severity.objects.get(slug=severity_slug, project=project)
    form = SeverityForm(request.POST, instance=instance, project=project)
    if (form.is_valid()):
        severity = form.save()
        return HttpResponse(json.dumps(
            {'error': False, 'color': severity.color, 'name': severity.name, 'proj_id': severity.id,
             'slug': severity.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
@check_project_admin
def severity_delete(request, slug, severity_slug):
    Severity.objects.get(
        slug=severity_slug, project=Project.objects.get(slug=slug, organization=request.user.organization)).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")

@active_user_required
@check_project_admin
def ticket_status(request, slug):
    ticket_status_list = TicketStatus.objects.filter(
        project=Project.objects.get(slug=slug, organization=request.user.organization)).order_by('order')
    return render(request, 'settings/ticket_status.html', {'slug': slug, 'ticket_status_list': ticket_status_list,
                                                           'notification_list': get_notification_list(request.user)})


@active_user_required
@check_project_admin
def ticket_status_default(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    TicketStatus.objects.bulk_create(
        [TicketStatus(name='New', slug=slugify('New'), color='#999999', project=project, order=1),
         TicketStatus(name='In progress', slug=slugify('In progress'), color='#729fcf',
                      project=project, order=2),
         TicketStatus(name='Ready for test', slug=slugify('Ready for test'),
                      color='#4e9a06', project=project, order=3),
         TicketStatus(name='Done', slug=slugify('Done'), color='#cc0000', project=project, order=4)]
         )
    if not project.task_statuses.filter(is_final=True):
        TicketStatus.objects.create(name='Archived', slug=slugify('Archived'), color='#5c3566',
                      project=project, is_final=True, order=5)
    messages.success(request, 'Default status are added to the ticket status page !')
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@active_user_required
@check_project_admin
def ticket_status_create(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    form = TicketStatusForm(request.POST, project=project)
    is_final = request.POST.get('is_final',False)
    if (form.is_valid()):
        ticket_status = form.save()
        if is_final:
            if not project.task_statuses.filter(is_final=True):
                ticket_status.is_final = True
                ticket_status.save()
            else:
                ticket = project.task_statuses.get(is_final=True)
                if ticket:
                    ticket.is_final = False
                    ticket.save()
                ticket_status.is_final = True
                ticket_status.save()
        else:
            ticket_statuses = project.task_statuses.all()
            if ticket_statuses and not ticket_statuses.filter(is_final=True):
                ticket_assign = ticket_statuses[len(ticket_statuses)-1]
                ticket_assign.is_final = True
                ticket_assign.save()
        return HttpResponse(json.dumps(
            {'error': False, 'color': ticket_status.color, 'name': ticket_status.name, 'id': ticket_status.id,
             'slug': ticket_status.slug,'is_final':is_final}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
@check_project_admin
def ticket_status_edit(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    instance = TicketStatus.objects.get(id=request.POST['id'], project=project)
    form = TicketStatusForm(request.POST, instance=instance, project=project)
    is_final = request.POST.get('is_final',False)
    if (form.is_valid()):
        ticket_status = form.save()
        if is_final:
            ticket = project.task_statuses.get(is_final=True)
            if ticket:
                ticket.is_final = False
                ticket.save()
            ticket_status.is_final = True
            ticket_status.save()
        return HttpResponse(json.dumps(
            {'error': False, 'color': ticket_status.color, 'name': ticket_status.name, 'proj_id': ticket_status.id,
             'slug': ticket_status.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
@check_project_admin
def ticket_status_delete(request, slug, ticket_slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    ticket = TicketStatus.objects.get(slug=ticket_slug, project=project)
    is_final = ticket.is_final
    ticket.delete()
    if is_final:
        ticket_statuses = project.task_statuses.all()
        if ticket_statuses:
            ticket_assign = ticket_statuses[len(ticket_statuses)-1]
            ticket_assign.is_final = True
            ticket_assign.save()

    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@active_user_required
@check_project_admin
def ticket_status_order(request, slug):
    prev = request.GET.get('prev',False)
    current = request.GET.get('current',False)
    print current,prev
    if prev and current:
        prev = int(prev)
        current = int(current)
        project=Project.objects.get(slug=slug, organization=request.user.organization)
        ticket_statuses = project.task_statuses.all().order_by('order')
        if prev > current:
            for ticket_status in ticket_statuses[current:prev+1]:
                if ticket_status.order-1 == prev :
                    ticket_status.order = current+1
                else:
                    ticket_status.order+=1
                ticket_status.save()
        else:
            for ticket_status in ticket_statuses[prev:current+1]:
                if ticket_status.order-1 == prev :
                    ticket_status.order=current+1
                else:
                    ticket_status.order-=1
                ticket_status.save()
    return HttpResponse("ok")


def password_reset(request, to_email):
    from_email = request.user.organization.slug + "@pietrack.com"
    to_email_dict = {'email': to_email}
    token_generator = default_token_generator
    email_template_name = 'email/reset_email.html'
    subject_template_name = 'email/reset_subject.txt'
    form = PasswordResetForm(to_email_dict)
    if form.is_valid():
        opts = {
            'use_https': request.is_secure(),
            'from_email': from_email,
            'email_template_name': email_template_name,
            'subject_template_name': subject_template_name,
            'request': request}
        form.save(**opts)


@active_user_required
@is_project_member
def project_team(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    dictionary = {'project': project, 'slug': slug, 'notification_list': get_notification_list(request.user)}
    return render(request, 'settings/team.html', dictionary)


@active_user_required
@check_project_admin
def create_member(request, slug):
    if request.method == 'POST':
        error_count = 0
        json_data = {}
        json_post_index = 0
        email_list = request.POST.getlist('email')
        designation_list = request.POST.getlist('designation')
        description = request.POST.get('description')
        post_dict = {'description': description}
        post_tuple = zip(email_list, designation_list)
        team_members = []
        project_obj = Project.objects.get(slug=slug, organization=request.user.organization)
        for email_iter, designation_iter in post_tuple:
            if email_iter != '':
                email_iter += '@' + request.user.organization.domain
            post_dict['email'] = email_iter
            post_dict['designation'] = designation_iter

            create_member_form = CreateMemberForm(post_dict, slug=slug, organization=request.user.organization)
            if len(email_list) == len(set(email_list)) or email_list.count('') > 0:
                if create_member_form.is_valid():
                    random_password = ''.join(
                        random.choice(string.digits) for _ in xrange(8))
                    new_user_obj = User(
                        email=post_dict['email'], username=post_dict['email'], password=random_password,
                        organization=request.user.organization,
                        pietrack_role='user')
                    team_members.append((new_user_obj, post_dict['designation']))
                    json_post_index += 1
                else:
                    error_count += 1
                    json_data[json_post_index] = create_member_form.errors
                    json_post_index += 1
            if len(email_list) != len(set(email_list)):
                json_data['emails'] = True

        if error_count == 0 and len(email_list) == len(set(email_list)):
            for user, designation in team_members:
                email = user.email
                subject = ' Invitation to join in the project "' + project_obj.name + '"'
                message = 'Dear User,\n Please login to your account in http://pietrack.com to know more details.\n' + \
                          request.POST.get('description')
                from_email = project_obj.organization.slug + "@pietrack.com"
                if User.objects.filter(email=user.email):
                    send_mail_old_user.delay(subject, message, from_email, email)
                    pass
                else:
                    user.save()
                    password_reset(request, email)
                user_obj = User.objects.get(email=email)
                project_obj.members.add(user_obj)
                project_obj.organization = request.user.organization
                role = Role.objects.get(slug=designation, project=project_obj)
                role.users.add(User.objects.get(email=email))
                role.save()
                project_obj.save()
                msg = " added " + user_obj.username + " as a team member"
                create_timeline.send(sender=request.user, content_object=user_obj, namespace=msg,
                                     event_type="member added", project=project_obj)
            json_data['error'] = False
        else:
            json_data['error'] = True
        messages.success(request, 'Successfully added project members !')
        return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        project_roles = Role.objects.filter(project__slug=slug, project__organization=request.user.organization)
        return render(request, 'settings/create_member.html', {'slug': slug, 'project_roles': project_roles,
                                                               'notification_list': get_notification_list(
                                                                   request.user)})


@active_user_required
@check_project_admin
def edit_member(request, slug):
    if request.POST:
        email = request.POST.get('email', False)
        role_slug = request.POST.get('designation', False)
        project = Project.objects.get(slug=slug, organization=request.user.organization)
        role = Role.objects.get(project=project, users__email=email)
        old_role = role.name
        member = role.users.get(email=email)
        role.users.remove(member)
        new_role = Role.objects.get(slug=role_slug, project=project)
        new_role.users.add(member)
        if (role != new_role):
            msg = " changed role of " + member.username + "'s  from " + old_role + " to " + str(new_role)
            create_timeline.send(sender=request.user, content_object=member, namespace=msg,
                                 event_type="member edited", project=project)
        return HttpResponse(True)
    elif request.GET.get('id', False):
        project_roles = Role.objects.filter(project__slug=slug, project__organization=request.user.organization)
        role = project_roles.get(users__id=request.GET.get('id'))
        member = role.users.get(id=request.GET.get('id'))
        return render(request, 'settings/create_member.html',
                      {'slug': slug, 'edit_project': True, 'project_roles': project_roles, 'mrole': role,
                       'member': member, 'notification_list': get_notification_list(request.user)})
    return HttpResponse("Invalid Request")


@active_user_required
@check_project_admin
def delete_member(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    result = False
    if request.GET.get('id', False):
        member = project.members.get(id=request.GET.get('id'))
        if member.pietrack_role != 'admin':
            project.members.remove(member)
            pass
        try:
            role = Role.objects.get(project=project, users__email=member.email)
            Timeline.objects.filter(user=member, project=project).delete()
            role.users.remove(member)
            result = True
            msg = "removed " + member.email + " from the project "
            create_timeline.send(sender=request.user, content_object=member, namespace=msg,
                                 event_type="member removed", project=project)
        except Exception as e:
            pass
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")


@active_user_required
@is_project_member
def member_roles(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    list_of_roles = Role.objects.filter(project=project)
    dictionary = {'list_of_roles': list_of_roles, 'slug': slug,
                  'notification_list': get_notification_list(request.user), 'project': project}

    return render(request, 'settings/member_roles.html', dictionary)


@active_user_required
@check_project_admin
def member_roles_default(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    Role.objects.bulk_create(
        [Role(name='Project Admin', slug=slugify('Project Admin'), project=project, is_project_admin=True),
         Role(name='UX Developer', slug=slugify('UX Developer'), project=project),
         Role(name='Web Designer', slug=slugify('Web Designer'), project=project),
         Role(name='Front-end Developer', slug=slugify('Front-end Developer'), project=project),
         Role(name='Back-end Developer', slug=slugify('Back-end Developer'), project=project)])
    roles = Role.objects.filter(is_project_admin=True)
    for role in roles:
        role.users.add(request.user)
        role.save()
    messages.success(request, 'Default user roles are added to the User roles page !')
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@active_user_required
@check_project_admin
def member_role_create(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    form = RoleForm(request.POST, project=project)
    if form.is_valid():
        role = form.save()
        json_data = {}
        if request.POST.get('is_project_admin', False):
            role.is_project_admin = True
            role.users.add(request.user)
            role.save()
            json_data['email'] = request.user.email
        msg = "created role " + role.name + " in the project "
        create_timeline.send(sender=request.user, content_object=role, namespace=msg,
                             event_type="role created", project=project)
        json_data.update({'error': False, 'role_id': role.id, 'role_name': role.name, 'slug': role.slug})
        return HttpResponse(json.dumps(json_data), content_type="application/json")

    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
@check_project_admin
def member_role_edit(request, slug, member_role_slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    instance = Role.objects.get(
        slug=member_role_slug, project=project)
    old_role = instance.name
    form = RoleForm(request.POST, instance=instance, project=project)
    if form.is_valid():
        role = form.save()
        msg = "renamed current role " + old_role + " to " + role.name
        create_timeline.send(sender=request.user, content_object=role, namespace=msg,
                             event_type="role renamed", project=project)
        return HttpResponse(json.dumps({'error': False, 'role_id': role.id, 'role_name': role.name, 'slug': role.slug}),
                            content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
@check_project_admin
def member_role_delete(request, slug, member_role_slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    role = Role.objects.get(slug=member_role_slug, project=project)
    for member in role.users.all():
        Timeline.objects.filter(user=member, project=project).delete()
        msg = "removed user " + str(member.username) + " from  project "
        create_timeline.send(sender=request.user, content_object=member, namespace=msg,
                             event_type="user deleted", project=project)
    project.members.remove(*role.users.filter(~Q(pietrack_role='admin')))
    role.delete()
    msg = "removed role " + role.name + " from this project "
    create_timeline.send(sender=request.user, content_object=project, namespace=msg,
                         event_type="role deleted", project=project)
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@active_user_required
@is_project_member
def tickets(request, slug):
    if Milestone.objects.filter(project__slug=slug, project__organization=request.user.organization).exists():
        milestone_slug = Milestone.objects.filter(project__slug=slug, project__organization=request.user.organization)[
            0].slug
        return HttpResponseRedirect(
            reverse('project:taskboard', kwargs={'slug': slug, 'milestone_slug': milestone_slug}))
    else:
        messages.warning(request, 'Please create a mile-stone to view tickets')
        return HttpResponseRedirect(reverse('project:milestone_display', kwargs={'slug': slug}))


@active_user_required
@is_project_member
def taskboard(request, slug, milestone_slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    milestone = Milestone.objects.get(slug=milestone_slug, project=project)
    ticket_status_list = TicketStatus.objects.filter(project=project).order_by('id')
    mem_details = []
    for member in project.members.all():
        try:
            mem_details.append(member)
        except:
            pass
    return render(request, 'project/taskboard.html',
                  {'ticket_status_list': ticket_status_list, 'slug': slug, 'milestone': milestone,
                   'project_members': mem_details, 'notification_list': get_notification_list(request.user)})


@active_user_required
@is_project_member
def update_taskboard_status(request, slug, status_slug, task_id):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    task = Ticket.objects.get(id=task_id, project=project)
    old_status = task.status.name
    ticket_status = TicketStatus.objects.get(
        slug=status_slug, project=project)
    task.status = ticket_status
    task.save()
    msg = "moved " + task.name + " from " + old_status + " to " + task.status.name
    create_timeline.send(sender=request.user, content_object=task, namespace=msg,
                         event_type="task moved", project=project)
    return HttpResponse("")


@active_user_required
@is_project_member
def load_tasks(request, slug, milestone_slug, status_slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    status = TicketStatus.objects.get(slug=status_slug, project=project)
    milestone = Milestone.objects.get(slug=milestone_slug, project=project)
    tasks = Ticket.objects.filter(status=status, milestone=milestone)

    paginator = Paginator(tasks, 10)
    page = request.GET.get('page')
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        pass
    except EmptyPage:
        pass
    return render_to_response('project/partials/task.html', {'tasks': tasks, 'milestone': milestone, 'slug': slug,
                                                             'notification_list': get_notification_list(request.user)})


@active_user_required
@is_project_member
def requirement_tasks(request, slug, milestone_slug, requirement_id):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    milestone = Milestone.objects.get(slug=milestone_slug, project=project)
    ticket_status_list = TicketStatus.objects.filter(project=project).order_by('id')
    return render(request, 'project/partials/requirement_tasks.html',
                  {'ticket_status_list': ticket_status_list, 'slug': slug, 'requirement_id': requirement_id,
                   'milestone': milestone, 'notification_list': get_notification_list(request.user)})


@active_user_required
@is_project_member
def requirement_tasks_more(request, slug, milestone_slug, status_slug, requirement_id):
    requirement = Requirement.objects.get(id=requirement_id)
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    milestone = Milestone.objects.get(slug=milestone_slug, project=project)
    tasks = requirement.tasks.filter(status__slug=status_slug)
    paginator = Paginator(tasks, 10)
    page = request.GET.get('page')
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        pass
    except EmptyPage:
        pass
    return render_to_response('project/partials/task.html', {'tasks': tasks, 'milestone': milestone, 'slug': slug,
                                                             'notification_list': get_notification_list(request.user)})


@active_user_required
@is_project_member
def task_details(request, slug, milestone_slug, task_id):
    project = Project.objects.get(slug=slug)
    task = Ticket.objects.get(id=task_id, milestone__slug=milestone_slug,
                              project__organization=request.user.organization)
    return render(request, 'task/Task_detail.html', {'task': task, 'slug': slug, 'project': project,
                                                     'notification_list': get_notification_list(request.user)})


@active_user_required
@is_project_member
def task_comment(request, slug, task_id):
    project = Project.objects.get(
        slug=slug, organization=request.user.organization)
    task = Ticket.objects.get(id=task_id, project=project)
    form = CommentForm(
        request.POST, task=task, user=request.user, project=project)

    if form.is_valid():
        comment = form.save()
        if request.GET.get('parent_id', False):
            comment.parent_id = request.GET.get('parent_id')

        if request.FILES.get('file'):
            attachment = Attachment.objects.create(
                uploaded_by=request.user, attached_file=request.FILES.get('file'), project=project)
            comment.attachments.add(attachment)
        comment.save()
        msg = "commented on " + task.name
        if request.GET.get('parent_id', False):
            msg = "gave reply to " + comment.parent.commented_by.username + "  on " + task.name
            create_timeline.send(sender=request.user, content_object=comment.parent.commented_by, namespace=msg,
                                 event_type="commented",
                                 project=project)
        else:
            create_timeline.send(sender=request.user, content_object=comment, namespace=msg, event_type="commented",
                                 project=project)
        return HttpResponse(
            render(request, 'task/partials/comment_add.html',
                   {'comment': comment, 'slug': slug, 'task': task, 'project': project,
                    'notification_list': get_notification_list(request.user)}))
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="json/application")


@active_user_required
@is_project_member
def task_comment_edit(request):
    project = Project.objects.get(slug=request.POST.get('slug'), organization=request.user.organization)
    task = Ticket.objects.get(id=request.POST.get('task_id'), project=project)
    comment = Comment.objects.get(id=request.POST.get('comment_id'))
    form = CommentForm(request.POST, task=task, user=request.user, project=project, instance=comment)
    if form.is_valid():
        form.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@active_user_required
@is_project_member
def task_edit(request, slug, milestone_slug, task_id):
    project_obj = Project.objects.get(slug=slug, organization=request.user.organization)
    task = Ticket.objects.get(id=task_id, project=project_obj, milestone__slug=milestone_slug)
    old_name = task.name
    old_assigned_to = task.assigned_to
    if request.POST:
        form = TaskForm(request.POST, user=request.user, project=task.project, instance=task)
        json_data = {}
        if form.is_valid():
            json_data['error'] = False
            new_task = form.save()
            msg = "updated task " + task.name + " details "
            if old_name != new_task.name:
                msg = "renamed task " + old_name + " to " + new_task.name + " "
                create_timeline.send(sender=request.user, content_object=new_task, namespace=msg,
                                     event_type="task renamed",
                                     project=project_obj)
            elif old_assigned_to != new_task.assigned_to:
                msg = "removed user" + old_assigned_to.username + " from " + new_task.name + " "
                create_timeline.send(sender=request.user, content_object=old_assigned_to, namespace=msg,
                                     event_type="user removed",
                                     project=project_obj)
                msg = "task " + new_task.name + " assigned to user" + new_task.assigned_to.username
                create_timeline.send(sender=request.user, content_object=new_task.assigned_to, namespace=msg,
                                     event_type="task assigned",
                                     project=project_obj)
        else:
            json_data['error'] = True
            json_data['form_errors'] = form.errors
        return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        requirement_list = project_obj.requirements.filter(milestone__slug=milestone_slug)
        ticket_status_list = TicketStatus.objects.filter(project=project_obj).order_by('id')
        assigned_to_list = []
        for member in project_obj.members.all():
            try:
                Role.objects.get(users__email=member.email, project=project_obj)
                assigned_to_list.append(member)
            except:
                pass
        return render(request, 'task/add_task.html', {'requirement_list': requirement_list,
                                                      'ticket_status_list': ticket_status_list,
                                                      'assigned_to_list': assigned_to_list, 'slug': slug,
                                                      'task': task, 'milestone': task.milestone}
                      )


@active_user_required
@is_project_member
def task_delete(request, slug, milestone_slug, task_id):
    marker = False
    try:
        Ticket.objects.get(id=task_id, project__slug=slug, project__organization=request.user.organization,
                           milestone__slug=milestone_slug).delete()
        marker = True
    finally:
        pass
    return HttpResponse(marker)


@active_user_required
@is_project_member
def delete_attachment(request, slug, task_id, attachment_id):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    attach = Attachment.objects.get(id=attachment_id, project=project)
    task = Ticket.objects.get(id=task_id)
    try:
        shutil.rmtree(
            os.path.abspath(os.path.join(attach.attached_file.path, os.pardir)))
        attach.delete()
        msg = " deleted attachment of " + task.name
        create_timeline.send(sender=request.user, content_object=task, namespace=msg, event_type="deleted",
                             project=project)
    except OSError as e:
        pass

    return HttpResponse(json.dumps({'result': True}), content_type="json/application")


@active_user_required
@is_project_member
def delete_task_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if comment.commented_by == request.user:
        task = comment.ticket
        project = comment.ticket.project
        for attachment in comment.attachments.all():
            comment.attachments.remove(attachment)
            attachment.delete()
        comment.delete()
        msg = " deleted comment of " + comment.ticket.name
        create_timeline.send(sender=request.user, content_object=task, namespace=msg, event_type="deleted",
                             project=project)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@active_user_required
@is_project_member
def milestone_display(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    milestones_list = Milestone.objects.filter(project=project)
    return render(request, 'project/milestones_list.html',
                  {'slug': slug, 'milestones_list': milestones_list, 'project': project,
                   'notification_list': get_notification_list(request.user)})


@active_user_required
@check_project_admin
def milestone_create(request, slug):
    if request.method == 'POST':
        json_data = {}
        milestone_dict = request.POST.copy()
        project = Project.objects.get(slug=slug, organization=request.user.organization)
        project_id = project.id
        milestone_dict['project'] = project_id
        milestone_form = MilestoneForm(request.user, milestone_dict)
        if milestone_form.is_valid():
            milestone = milestone_form.save()
            msg = " created milestone " + milestone.name
            create_timeline.send(sender=request.user, content_object=milestone, namespace=msg,
                                 event_type="milestone created", project=project)
            json_data['error'] = False
            messages.success(request, 'Successfully created Milestone - ' + str(milestone.name) + ' !')
            return HttpResponse(json.dumps(json_data), content_type='application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = milestone_form.errors
            return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        return render(request, 'project/milestone.html',
                      {'slug': slug, 'notification_list': get_notification_list(request.user)})


@active_user_required
@check_project_admin
def milestone_edit(request, slug, milestone_slug):
    milestone_obj = Milestone.objects.get(project__slug=slug, slug=milestone_slug,
                                          project__organization=request.user.organization)
    old_name = milestone_obj.name
    if request.method == 'POST':
        json_data = {}
        milestone_dict = request.POST.copy()
        project_id = milestone_obj.project.id
        milestone_dict['project'] = project_id
        milestone_form = MilestoneForm(
            request.user, milestone_dict, instance=milestone_obj)
        if milestone_form.is_valid():

            milestone = milestone_form.save()
            json_data['error'] = False
            messages.success(request, 'Successfully updated Milestone - ' + str(milestone_obj.name) + ' !')
            if old_name != milestone.name:
                msg = "renamed milestone " + old_name + " to " + milestone.name
            else:
                msg = "milestone " + milestone.name + " details updated"
            create_timeline.send(sender=request.user, content_object=milestone, namespace=msg,
                                 event_type="milestone edited", project=milestone.project)

            return HttpResponse(json.dumps(json_data), content_type='application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = milestone_form.errors
            return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        return render(request, 'project/milestone.html', {'milestone_obj': milestone_obj, 'slug': slug,
                                                          'notification_list': get_notification_list(request.user)})


@active_user_required
@check_project_admin
def milestone_delete(request, slug, milestone_slug):
    milestone = Milestone.objects.get(project__slug=slug, slug=milestone_slug,
                                      project__organization=request.user.organization)
    timeline_list = [milestone]
    timeline_list.extend(milestone.requirements.all())
    task_list = milestone.tasks.all()
    timeline_list.extend(task_list)
    for task in task_list:
        timeline_list.extend(task.ticket_comments.all())

    for timeline in timeline_list:
        content_type = ContentType.objects.get_for_model(timeline)
        Timeline.objects.filter(content_type__id=content_type.id, object_id=timeline.id).delete()
    msg = " deleted milestone " + milestone.name
    create_timeline.send(sender=request.user, content_object=milestone.project, namespace=msg,
                         event_type="milestone deleted", project=milestone.project)
    milestone.delete()
    messages.success(request, 'Successfully deleted Milestone - ' + str(milestone) + ' !')
    return HttpResponse(json.dumps({'result': True}), content_type='application/json')


@active_user_required
@check_project_admin
def project_edit(request, slug):
    project_obj = Project.objects.get(slug=slug, organization=request.user.organization)
    milestone_list = Milestone.objects.filter(project=project_obj)
    member_dict = {}
    for member_iter in project_obj.members.all():
        member_dict[member_iter.email] = [
            role.name for role in member_iter.user_roles.all()]
    msg = " project details updated "
    create_timeline.send(sender=request.user, content_object=project_obj, namespace=msg,
                         event_type="milestone deleted", project=project_obj)
    messages.success(request, 'Successfully updated project - ' + str(project_obj.name) + ' !')
    return render(request, 'project/project_edit.html',
                  {'milestone_list': milestone_list, 'member_dict': member_dict, 'project_slug': slug})


@active_user_required
@check_project_admin
def requirement_create(request, slug, milestone_slug):
    project_obj = Project.objects.get(slug=slug, organization=request.user.organization)
    if request.POST:
        json_data = {}
        requirement_form = RequirementForm(request.POST)
        if requirement_form.is_valid():
            name = request.POST.get('name')
            milestone_obj = Milestone.objects.get(
                id=request.POST.get('milestone'))
            requirement = Requirement.objects.create(name=name, slug=slugify(name), description=request.POST.get(
                'description'), project=project_obj, milestone=milestone_obj)

            msg = " created requirement " + requirement.name
            create_timeline.send(sender=request.user, content_object=requirement, namespace=msg,
                                 event_type="requirement_form", project=project_obj)

            json_data['error'] = False
            messages.success(request, 'Successfully added requirement - ' + str(requirement.name) + ' !')
            return HttpResponse(json.dumps(json_data), content_type='application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = requirement_form.errors
            return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        milestone = project_obj.milestones.get(slug=milestone_slug)
        return render(request, 'project/requirement.html',
                      {'milestone': milestone, 'slug': slug, 'notification_list': get_notification_list(request.user)})


@active_user_required
@check_project_admin
def requirement_edit(request, slug, milestone_slug, requirement_slug):
    project_obj = Project.objects.get(slug=slug, organization=request.user.organization)
    milestone = Milestone.objects.get(id=milestone_slug, project=project_obj)
    requirement_obj = Requirement.objects.get(slug=requirement_slug, milestone=milestone)
    if request.POST:
        json_data = {}
        requirement_form = RequirementForm(request.POST, instance=requirement_obj)
        if requirement_form.is_valid():
            requirement_form.save()
            msg = " requirement " + requirement_obj.name + " was updated "
            create_timeline.send(sender=request.user, content_object=requirement_obj, namespace=msg,
                                 event_type="requirement_form", project=project_obj)
            json_data['error'] = False
            messages.success(request, 'Successfully updated your requirement - ' + str(requirement_obj.name) + ' !')
            return HttpResponse(json.dumps(json_data), content_type='application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = requirement_form.errors
            return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:

        context = {'milestone': milestone, 'requirement_obj': requirement_obj, 'slug': slug,
                   'notification_list': get_notification_list(request.user)}
        return render(request, 'project/requirement.html', context)


@active_user_required
@check_project_admin
def requirement_delete(request, slug, milestone_slug, id):
    project_object = Project.objects.get(slug=slug, organization=request.user.organization)
    milestone = Milestone.objects.get(slug=milestone_slug, project=project_object)
    requirement_object = Requirement.objects.get(id=id, milestone=milestone)
    requirement_name = requirement_object.name
    timeline_list = [requirement_object]
    task_list = requirement_object.tasks.all()
    timeline_list.extend(task_list)
    for task in task_list:
        timeline_list.extend(task.ticket_comments.all())
    for timeline in timeline_list:
        content_type = ContentType.objects.get_for_model(timeline)
        Timeline.objects.filter(content_type__pk=content_type.id, object_id=timeline.id).delete()
    requirement_object.delete()
    msg = " deleted requirement " + requirement_name
    create_timeline.send(sender=request.user, content_object=milestone, namespace=msg,
                         event_type="requirement_form", project=project_object)
    return HttpResponseRedirect(reverse('project:taskboard', kwargs={'milestone_slug': milestone_slug, 'slug': slug}))
