from django.shortcuts import render, redirect, render_to_response
from piebase.models import User, Project, Priority, Severity, TicketStatus, Ticket, Requirement, Attachment, Role, \
    Milestone
from forms import CreateProjectForm, PriorityForm, SeverityForm, TicketStatusForm, RoleForm, CommentForm, \
    CreateMemberForm, PasswordResetForm, MilestoneForm, RequirementForm
import json
import random
import string
import os
import shutil
from PIL import Image
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from .tasks import send_mail_old_user
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from signals import create_timeline

# for messages in views and templates
from django.contrib import messages

user_login_required = user_passes_test(
    lambda user: user.is_active, login_url='/')


def active_user_required(view_func):
    decorated_view_func = login_required(
        user_login_required(view_func), login_url='/')
    return decorated_view_func


@active_user_required
def create_project(request):
    if (request.method == "POST"):
        img = False
        if (request.FILES.get('logo', False)):
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
            project_obj = form.save()
            if (request.FILES.get('logo', False)):
                project_obj.logo = request.FILES.get('logo')
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
    dict_items = {'projects_list': projects_list}
    return render(request, template_name, dict_items)


@active_user_required
def project_detail(request, slug):
    template_name = 'project/project_description.html'
    project_object = Project.objects.get(slug=slug, organization=request.user.organization)
    project_members = project_object.members.all()
    dict_items = {'project_object': project_object,
                  'project_members': project_members,
                  'slug': slug
                  }
    return render(request, template_name, dict_items)


@active_user_required
def project_details(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    dictionary = {'project': project, 'slug': slug}
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
def delete_project(request, id):
    try:
        project = Project.objects.get(id=id, organization=request.user.organization)
        project.delete()
    except OSError as e:
        pass
    messages.success(request, 'Successfully deleted Project - ' + str(project) + ' !')
    return redirect("project:list_of_projects")


@active_user_required
def priorities(request, slug):
    priority_list = Priority.objects.filter(
        project=Project.objects.get(slug=slug, organization=request.user.organization))
    return render(request, 'settings/priorities.html', {'slug': slug, 'priority_list': priority_list})


@active_user_required
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
def priority_delete(request, slug, priority_slug):
    Priority.objects.get(
        slug=priority_slug, project=Project.objects.get(slug=slug, organization=request.user.organization)).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@active_user_required
def severities(request, slug):
    severity_list = Severity.objects.filter(
        project=Project.objects.get(slug=slug, organization=request.user.organization))
    return render(request, 'settings/severities.html', {'slug': slug, 'severity_list': severity_list})


@active_user_required
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
def severity_delete(request, slug, severity_slug):
    Severity.objects.get(
        slug=severity_slug, project=Project.objects.get(slug=slug, organization=request.user.organization)).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@active_user_required
def ticket_status(request, slug):
    ticket_status_list = TicketStatus.objects.filter(
        project=Project.objects.get(slug=slug, organization=request.user.organization))
    return render(request, 'settings/ticket_status.html', {'slug': slug, 'ticket_status_list': ticket_status_list})


@active_user_required
def ticket_status_create(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    form = TicketStatusForm(request.POST, project=project)
    if (form.is_valid()):
        ticket_status = form.save()
        return HttpResponse(json.dumps(
            {'error': False, 'color': ticket_status.color, 'name': ticket_status.name, 'proj_id': ticket_status.id,
             'slug': ticket_status.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
def ticket_status_edit(request, slug, ticket_slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    instance = TicketStatus.objects.get(slug=ticket_slug, project=project)
    form = TicketStatusForm(request.POST, instance=instance, project=project)
    if (form.is_valid()):
        ticket_status = form.save()
        return HttpResponse(json.dumps(
            {'error': False, 'color': ticket_status.color, 'name': ticket_status.name, 'proj_id': ticket_status.id,
             'slug': ticket_status.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
def ticket_status_delete(request, slug, ticket_slug):
    ticket = TicketStatus.objects.get(
        slug=ticket_slug, project=Project.objects.get(slug=slug, organization=request.user.organization))
    ticket.delete()
    messages.success(request, 'Successfully deleted Ticket - ' + str(ticket) + ' !')
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


def password_reset(request, to_email):
    from_email = request.user.organization.slug+"@pietrack.com"
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
def project_team(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    mem_details = []
    for member in project.members.all():
        try:
            mem_details.append((member, Role.objects.get(users__email=member.email, project=project)))
        except:
            pass
    dictionary = {'project': project, 'mem_details': mem_details, 'slug': slug}
    return render(request, 'settings/team.html', dictionary)


@active_user_required
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
        for email_iter, designation_iter in post_tuple:
            post_dict['email'] = email_iter
            post_dict['designation'] = designation_iter
            create_member_form = CreateMemberForm(post_dict, slug=slug, organization=request.user.organization)
            if len(email_list) == len(set(email_list)) or email_list.count('') > 0:
                if create_member_form.is_valid() and email_list.count('') == 0:
                    email = post_dict['email']
                    designation = post_dict['designation']
                    description = post_dict['description']
                    organization_obj = request.user.organization
                    project_obj = Project.objects.get(slug=slug, organization=request.user.organization)
                    subject = ' Invitation to join in the project "'+project_obj.name+'"'
                    message = 'Dear User,\n Please login to your account in http://pietrack.com to know more details.\n'
                    from_email =  project_obj.organization.slug+"@pietrack.com"
                    if User.objects.filter(email=email).exists():
                        send_mail_old_user.delay(subject, message, from_email, email)
                        pass
                    else:
                        random_password = ''.join(
                            random.choice(string.digits) for _ in xrange(8))
                        new_user_obj = User.objects.create_user(
                            email=email, username=email, password=random_password, organization=organization_obj,
                            pietrack_role='user')
                        password_reset(request, email_iter)
                    
                    user_obj = User.objects.get(email=email)
                    project_obj.members.add(user_obj)
                    project_obj.organization = organization_obj
                    role = Role.objects.get(slug=designation, project=project_obj)
                    role.users.add(User.objects.get(email=email))
                    role.save()
                    project_obj.save()






                    msg = " added " + user_obj.username + " as a team member"
                    create_timeline.send(sender=request.user, content_object=user_obj, namespace=msg,
                                         event_type="member added", project=project_obj)
                else:
                    error_count += 1
                    json_data[json_post_index] = create_member_form.errors
                    json_post_index += 1
            if len(email_list) != len(set(email_list)) and email_list.count('') < 2:
                json_data['emails'] = True

        if error_count == 0 and len(email_list) == len(set(email_list)):
            json_data['error'] = False
        else:
            json_data['error'] = True
        messages.success(request, 'Successfully added project members !')
        return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        project_roles = Role.objects.filter(project__slug=slug, project__organization=request.user.organization)
        return render(request, 'settings/create_member.html', {'slug': slug, 'project_roles': project_roles})


@active_user_required
def edit_member(request, slug):
    if request.POST:
        email = request.POST.get('email', False)
        role_slug = request.POST.get('designation', False)
        project = Project.objects.get(slug=slug, organization=request.user.organization)
        role = Role.objects.get(project=project, users__email=email)
        member = role.users.get(email=email)
        role.users.remove(member)
        new_role = Role.objects.get(slug=role_slug, project=project)
        new_role.users.add(member)
        return HttpResponse(True)
    elif request.GET.get('id', False):
        project_roles = Role.objects.filter(project__slug=slug, project__organization=request.user.organization)
        role = project_roles.get(users__id=request.GET.get('id'))
        member = role.users.get(id=request.GET.get('id'))
        return render(request, 'settings/create_member.html',
                      {'slug': slug, 'edit_project': True, 'project_roles': project_roles, 'mrole': role,
                       'member': member})
    return HttpResponse("Invalid Request")


@active_user_required
def delete_member(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    result = False
    if request.GET.get('id', False):
        member = project.members.get(id=request.GET.get('id'))
        if member.pietrack_role != 'admin':
            project.members.remove(member)
        role = Role.objects.get(project=project, users__email=member.email)
        role.users.remove(member)
        result = True
    return HttpResponse(json.dumps({'result': result}), content_type="application/json")


@active_user_required
def member_roles(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    list_of_roles = Role.objects.filter(project=project)
    dictionary = {'list_of_roles': list_of_roles, 'slug': slug}
    return render(request, 'settings/member_roles.html', dictionary)


@active_user_required
def member_role_create(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    form = RoleForm(request.POST, project=project)
    if form.is_valid():
        role = form.save()
        return HttpResponse(json.dumps({'error': False, 'role_id': role.id, 'role_name': role.name, 'slug': role.slug}),
                            content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
def member_role_edit(request, slug, member_role_slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    instance = Role.objects.get(
        slug=member_role_slug, project=project)
    form = RoleForm(request.POST, instance=instance, project=project)
    if form.is_valid():
        role = form.save()
        return HttpResponse(json.dumps({'error': False, 'role_id': role.id, 'role_name': role.name, 'slug': role.slug}),
                            content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@active_user_required
def member_role_delete(request, slug, member_role_slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    role=Role.objects.get(slug=member_role_slug, project=project)
    project.members.remove(*role.users.all())
    role.delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@active_user_required
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
def taskboard(request, slug, milestone_slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    milestone = Milestone.objects.get(slug=milestone_slug, project=project)
    ticket_status_list = TicketStatus.objects.filter(project=project)
    mem_details = []
    for member in project.members.all():
        try:
            mem_details.append(member)
        except:
            pass
    return render(request, 'project/taskboard.html',
                  {'ticket_status_list': ticket_status_list, 'slug': slug, 'milestone': milestone,
                   'project_members': mem_details})


@active_user_required
def update_taskboard_status(request, slug, status_slug, task_id):
    task = Ticket.objects.get(id=task_id)
    ticket_status = TicketStatus.objects.get(
        slug=status_slug, project=Project.objects.get(slug=slug, organization=request.user.organization))
    task.status = ticket_status
    task.save()
    return HttpResponse("")


@active_user_required
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
    return render_to_response('project/partials/task.html', {'tasks': tasks, 'milestone': milestone, 'slug': slug})


@active_user_required
def requirement_tasks(request, slug, milestone_slug, requirement_id):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    milestone = Milestone.objects.get(slug=milestone_slug, project=project)
    ticket_status_list = TicketStatus.objects.filter(project=project)
    return render(request, 'project/partials/requirement_tasks.html',
                  {'ticket_status_list': ticket_status_list, 'slug': slug, 'requirement_id': requirement_id,
                   'milestone': milestone})


@active_user_required
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
    return render_to_response('project/partials/task.html', {'tasks': tasks, 'milestone': milestone, 'slug': slug})


@active_user_required
def task_details(request, slug, milestone_slug, task_id):
    task = Ticket.objects.get(id=task_id, milestone__slug=milestone_slug,
                              project__organization=request.user.organization)
    return render(request, 'task/Task_detail.html', {'task': task, 'slug': slug})


@active_user_required
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
        create_timeline.send(sender=request.user, content_object=comment, namespace=msg, event_type="commented",
                             project=project)
        return HttpResponse(
            render_to_response('task/partials/comment_add.html', {'comment': comment, 'slug': slug, 'task': task}))
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="json/application")


@active_user_required
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
def milestone_display(request, slug):
    project = Project.objects.get(slug=slug, organization=request.user.organization)
    milestones_list = Milestone.objects.filter(project=project)
    return render(request, 'project/milestones_list.html',
                  {'slug': slug, 'milestones_list': milestones_list, 'project': project})


@active_user_required
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
        return render(request, 'project/milestone.html', {'slug': slug})


@active_user_required
def milestone_edit(request, slug, milestone_slug):
    milestone_obj = Milestone.objects.get(project__slug=slug, slug=milestone_slug,
                                          project__organization=request.user.organization)
    if request.method == 'POST':
        json_data = {}
        milestone_dict = request.POST.copy()
        project_id = milestone_obj.project.id
        milestone_dict['project'] = project_id
        milestone_form = MilestoneForm(
            request.user, milestone_dict, instance=milestone_obj)
        if milestone_form.is_valid():
            milestone_form.save()
            json_data['error'] = False
            messages.success(request, 'Successfully updated Milestone - ' + str(milestone_obj.name) + ' !')
            return HttpResponse(json.dumps(json_data), content_type='application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = milestone_form.errors
            return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        return render(request, 'project/milestone.html', {'milestone_obj': milestone_obj, 'slug': slug})


@active_user_required
def milestone_delete(request, slug, milestone_slug):
    milestone = Milestone.objects.get(project__slug=slug, slug=milestone_slug,
                                      project__organization=request.user.organization)
    milestone.delete()
    messages.success(request, 'Successfully deleted Milestone - ' + str(milestone) + ' !')
    return HttpResponse(json.dumps({'result': True}), content_type='application/json')


@active_user_required
def project_edit(request, slug):
    milestone_list = Milestone.objects.all()
    project_obj = Project.objects.get(slug=slug)
    member_dict = {}
    for member_iter in project_obj.members.all():
        member_dict[member_iter.email] = [
            role.name for role in member_iter.user_roles.all()]
    messages.success(request, 'Successfully updated project - ' + str(project_obj.name) + ' !')
    return render(request, 'project/project_edit.html',
                  {'milestone_list': milestone_list, 'member_dict': member_dict, 'project_slug': slug})


@active_user_required
def requirement_create(request, slug):
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
        milestone = project_obj.milestones.all()
        return render(request, 'project/requirement.html', {'milestone': milestone, 'slug': slug})


@active_user_required
def requirement_edit(request, slug, milestone_slug, requirement_slug):
    project_obj = Project.objects.get(slug=slug, organization=request.user.organization)
    milestone = Milestone.objects.get(id=milestone_slug, project=project_obj)
    requirement_obj = Requirement.objects.get(slug=requirement_slug, milestone=milestone)
    if request.POST:
        json_data = {}
        requirement_form = RequirementForm(request.POST, instance=requirement_obj)
        if requirement_form.is_valid():
            requirement_form.save()

            json_data['error'] = False
            messages.success(request, 'Successfully updated your requirement - '+str(requirement_obj.name)+ ' !')
            return HttpResponse(json.dumps(json_data), content_type='application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = requirement_form.errors
            return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        milestone = project_obj.milestones.all()
        context = {'milestone': milestone, 'requirement_obj': requirement_obj, 'slug': slug}
        return render(request, 'project/requirement.html', context)

