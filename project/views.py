from django.shortcuts import render, redirect,render_to_response
from piebase.models import Project, Priority, Severity, TicketStatus, Ticket, Comment,Requirement
from forms import CreateProjectForm, PriorityForm, SeverityForm, TicketStatusForm, RoleForm
import json
import random
import string
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from piebase.models import User, Project, Organization, Role, Milestone, Requirement
from forms import CreateProjectForm, CreateMemberForm, PasswordResetForm, MilestoneForm, RequirementForm
from .tasks import send_mail_old_user
from django.core import serializers

from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage




@login_required
def create_project(request):
    if(request.method == "POST"):
        organization = request.user.organization
        form = CreateProjectForm(request.POST, organization=organization)
        if(form.is_valid()):
            slug = slugify(request.POST['name'])
            project_obj = Project.objects.create(name=request.POST['name'], slug=slug, description=request.POST[
                                                 'description'], modified_date=timezone.now(), organization=organization)
            project_obj.members.add(request.user)
            project_obj.save()
            json_data = {'error': False, 'errors': form.errors, 'slug': slug}
            return HttpResponse(json.dumps(json_data), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")
    return render(request, 'project/create_project.html')


@login_required
def list_of_projects(request):
    template_name = 'project/projects_list.html'
    projects_list = Project.objects.filter(members__email=request.user)
    dict_items = {'projects_list': projects_list}
    return render(request, template_name, dict_items)


@login_required
def project_detail(request, slug):
    template_name = 'project/project_description.html'
    project_object = Project.objects.get(slug=slug)
    project_members = project_object.members.all()
    dict_items = {'project_object': project_object, 'project_members': project_members}
    return render(request, template_name, dict_items)


@login_required
def project_details(request, slug):
    project = Project.objects.get(slug=slug)
    dictionary = {'project': project, 'slug': slug}
    template_name = 'project/project_project_details.html'

    if(request.method == 'POST'):
        organization = request.user.organization
        form = CreateProjectForm(request.POST, organization=organization)

        if(form.is_valid()):
            slug = slugify(request.POST['name'])
            project = Project.objects.get(
                slug=request.POST['oldname'], organization=organization)
            project.name = request.POST['name']
            project.slug = slug
            project.modified_date = timezone.now()
            project.save()
            return HttpResponse(json.dumps({'error': False, 'slug': slug}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")

    return render(request, template_name, dictionary)


@login_required
def delete_project(request, id):
    Project.objects.get(id=id).delete()
    return redirect("project:list_of_projects")


@login_required
def priorities(request, slug):
    priority_list = Priority.objects.filter(
    project=Project.objects.get(slug=slug))
    return render(request, 'settings/priorities.html', {'slug': slug, 'priority_list': priority_list})


@login_required
def priority_create(request, slug):
    project = Project.objects.get(slug=slug)
    form = PriorityForm(request.POST, project=project)
    if(form.is_valid()):
        priority = form.save()
        return HttpResponse(json.dumps({'error': False, 'color': priority.color, 'name': priority.name, 'proj_id': priority.id, 'slug': priority.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@login_required
def priority_edit(request, slug, priority_slug):
    project = Project.objects.get(slug=slug)
    instance = Priority.objects.get(slug=priority_slug, project=project)
    form = PriorityForm(request.POST, instance=instance,project=project)
    if(form.is_valid()):
        priority = form.save()
        return HttpResponse(json.dumps({'error': False, 'color': priority.color, 'name': priority.name, 'proj_id': priority.id, 'slug': priority.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@login_required
def priority_delete(request, slug, priority_slug):
    Priority.objects.get(
        slug=priority_slug, project=Project.objects.get(slug=slug)).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@login_required
def severities(request, slug):
    severity_list = Severity.objects.filter(
        project=Project.objects.get(slug=slug))
    return render(request, 'settings/severities.html', {'slug': slug, 'severity_list': severity_list})


@login_required
def severity_create(request, slug):
    project = Project.objects.get(slug=slug)
    form = SeverityForm(request.POST, project=project)
    if(form.is_valid()):
        severity = form.save()
        return HttpResponse(json.dumps({'error': False, 'color': severity.color, 'name': severity.name, 'proj_id': severity.id, 'slug': severity.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@login_required
def severity_edit(request, slug, severity_slug):
    project = Project.objects.get(slug=slug)
    instance = Severity.objects.get(slug=severity_slug, project=project)
    form = SeverityForm(request.POST, instance=instance, project=project)
    if(form.is_valid()):
        severity = form.save()
        return HttpResponse(json.dumps({'error': False, 'color': severity.color, 'name': severity.name, 'proj_id': severity.id, 'slug': severity.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@login_required
def severity_delete(request, slug, severity_slug):
    Severity.objects.get(
        slug=severity_slug, project=Project.objects.get(slug=slug)).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


@login_required
def ticket_status(request, slug):
    ticket_status_list = TicketStatus.objects.filter(
        project=Project.objects.get(slug=slug))
    return render(request, 'settings/ticket_status.html', {'slug': slug, 'ticket_status_list': ticket_status_list})


@login_required
def ticket_status_create(request, slug):
    project = Project.objects.get(slug=slug)
    form = TicketStatusForm(request.POST, project=project)
    if(form.is_valid()):
        ticket_status = form.save()
        return HttpResponse(json.dumps({'error': False, 'color': ticket_status.color, 'name': ticket_status.name, 'proj_id': ticket_status.id, 'slug': ticket_status.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@login_required
def ticket_status_edit(request, slug, ticket_slug):
    project = Project.objects.get(slug=slug)
    instance = TicketStatus.objects.get(slug=ticket_slug, project=project)
    form = TicketStatusForm(request.POST, instance=instance, project=project)
    if(form.is_valid()):
        ticket_status = form.save()
        return HttpResponse(json.dumps({'error': False, 'color': ticket_status.color, 'name': ticket_status.name, 'proj_id': ticket_status.id, 'slug': ticket_status.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@login_required
def ticket_status_delete(request, slug, ticket_slug):
    TicketStatus.objects.get(
        slug=ticket_slug, project=Project.objects.get(slug=slug)).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")


def password_reset(request, to_email):
    from_email = 'dineshmcmf@gmail.com'
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


@login_required
def project_team(request, slug):
    project = Project.objects.get(slug=slug)
    mem_details = []
    for member in project.members.exclude(email=request.user.email):
        mem_details.append(
            (member, Role.objects.get(users__email=member.email)))
    dictionary = {'project_id': project.id,
                  'mem_details': mem_details, 'slug': slug}
    return render(request, 'settings/team.html', dictionary)


@login_required
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
            create_member_form = CreateMemberForm(post_dict)
            if create_member_form.is_valid():
                email = post_dict['email']
                designation = post_dict['designation']
                description = post_dict['description']
                organization_obj = request.user.organization
                if User.objects.filter(email=email).exists():
                    send_mail_old_user.delay(email)
                    pass
                else:
                    random_password = ''.join(
                        random.choice(string.digits) for _ in xrange(8))
                    new_user_obj = User.objects.create_user(
                        email=email, username=email, password=random_password, organization=organization_obj, pietrack_role='user')
                    password_reset(request, email_iter)
                project_obj = Project.objects.get(slug=slug)
                user_obj = User.objects.get(email=email)
                project_obj.members.add(user_obj)
                project_obj.organization = organization_obj
                project_obj.save()

                random_slug = ''.join(
                    random.choice(string.ascii_letters + string.digits) for _ in xrange(10))
                role_obj = Role.objects.create(
                    name=designation, slug=random_slug, project=project_obj)
                role_obj.users.add(user_obj)
                role_obj.save()
            else:
                error_count += 1
            json_data[json_post_index] = create_member_form.errors
            json_post_index += 1
        if error_count == 0:
            json_data['error'] = False
        else:
            json_data['error'] = True
        return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        return render(request, 'settings/create_member.html')


@login_required
def member_roles(request, slug):
    project = Project.objects.get(slug=slug)
    list_of_roles = Role.objects.filter(project=project)
    dictionary = {'list_of_roles': list_of_roles, 'slug': slug}
    return render(request, 'settings/member_roles.html', dictionary)


@login_required
def member_role_create(request, slug):
    project = Project.objects.get(slug=slug)
    form = RoleForm(request.POST, project=project)
    if(form.is_valid()):
        role = form.save()
        return HttpResponse(json.dumps({'error': False, 'role_id': role.id, 'role_name': role.name, 'slug': role.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@login_required
def member_role_edit(request, slug, member_role_slug):
    project=Project.objects.get(slug=slug)
    instance = Role.objects.get(
        slug=member_role_slug, project=project)
    form = RoleForm(request.POST, instance=instance, project=project)
    if(form.is_valid()):
        role = form.save()
        return HttpResponse(json.dumps({'error': False, 'role_id': role.id, 'role_name': role.name, 'slug': role.slug}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'error': True, 'errors': form.errors}), content_type="application/json")


@login_required
def member_role_delete(request, slug, member_role_slug):
    project = Project.objects.get(slug=slug)
    Role.objects.get(slug=member_role_slug, project=project).delete()
    return HttpResponse(json.dumps({'error': False}), content_type="application/json")

def taskboard(request,slug,milestone_name):
    project = Project.objects.get(slug=slug)
    milestone = Milestone.objects.get(name=milestone_name,project=project)
    ticket_status_list = TicketStatus.objects.filter(project=project)
    return render(request,'project/taskboard.html',{'ticket_status_list':ticket_status_list,'slug':slug,'milestone':milestone})

def update_taskboard(request,slug,status_slug,task_id):
    task = Ticket.objects.get(id=task_id)
    ticket_status = TicketStatus.objects.get(slug=status_slug,project=Project.objects.get(slug=slug))
    task.status = ticket_status
    task.save()
    return HttpResponse("")

def load_tasks(request,slug,milestone_name,status_name):
    project = Project.objects.get(slug=slug)
    status = TicketStatus.objects.get(name=status_name,project=project)
    milestone = Milestone.objects.get(name=milestone_name,project=project)
    tasks = Ticket.objects.filter(status=status,milestone=milestone) 

    paginator = Paginator(tasks, 10)
    page = request.GET.get('page')
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        pass
    except EmptyPage:
        pass
    return render_to_response('project/partials/task.html',{'tasks':tasks})

   
def task_comment_count(request,slug,ticket_id):
    count = Comment.objects.filter(ticket__id=ticket_id).count()
    return HttpResponse(json.dumps({'count':count}),content_type="application/json")

def requirement_tasks(request,slug,milestone_name,requirement_id):
    project = Project.objects.get(slug=slug)
    milestone = Milestone.objects.get(name=milestone_name,project=project)
    ticket_status_list = TicketStatus.objects.filter(project=project)
    return render(request,'project/partials/requirement_tasks.html',{'ticket_status_list':ticket_status_list,'slug':slug,'milestone':milestone})


@login_required
def milestone_create(request, slug):
    if request.method == 'POST':
        milestone_form = MilestoneForm(request.POST)
        json_data = {}
        if milestone_form.is_valid():
            project_obj = Project.objects.get(slug = slug)
            name = request.POST.get('name')
            # modified date is duplicate, should be changed
            Milestone.objects.create(name = name, slug = name, project = project_obj, estimated_start = request.POST.get('estimated_start'), 
                    modified_date = request.POST.get('estimated_finish'), estimated_finish = request.POST.get('estimated_finish'), status = request.POST.get('status'))
            json_data['error'] = False
            return HttpResponse(json.dumps(json_data), content_type = 'application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = milestone_form.errors
            return HttpResponse(json.dumps(json_data), content_type = 'application/json')
    else:
        return render(request, 'project/milestone.html')

@login_required
def milestone_edit(request, slug):
    milestone_obj = Milestone.objects.get(slug = slug)
    if request.method == 'POST':
        json_data = {}
        milestone_dict = request.POST.copy()
        project_id = milestone_obj.project.id
        milestone_dict['project'] = project_id
        milestone_form = MilestoneForm(request.user, milestone_dict, instance = milestone_obj)
        if milestone_form.is_valid():
            milestone_form.save()
            json_data['error'] = False
            return HttpResponse(json.dumps(json_data), content_type = 'application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = milestone_form.errors
            return HttpResponse(json.dumps(json_data), content_type = 'application/json')
    else:
        return render(request, 'project/milestone.html', {'milestone_obj': milestone_obj})


@login_required
def milestone_delete(request, slug):
    Milestone.objects.get(slug = slug).delete()
    return HttpResponse(json.dumps({'error': False}))


@login_required
def project_edit(request, slug):
    milestone_list = Milestone.objects.all()
    project_obj = Project.objects.get(slug = slug)
    member_dict = {}
    for member_iter in project_obj.members.all():
        member_dict[member_iter.email] = [role.name for role in member_iter.user_roles.all()]
    return render(request, 'project/project_edit.html', {'milestone_list': milestone_list, 'member_dict': member_dict, 'project_slug': slug})


@login_required
def requirement_create(request, slug):
    project_obj = Project.objects.get(slug=slug)
    if request.POST:
        json_data = {}
        requirement_form = RequirementForm(request.POST)
        if requirement_form.is_valid():
            name = request.POST.get('name')
            milestone_obj = Milestone.objects.get(id=request.POST.get('milestone'))
            Requirement.objects.create(name=name, slug=name, description=request.POST.get('description'), project=project_obj, milestone=milestone_obj)
            json_data['error'] = False
            return HttpResponse(json.dumps(json_data), content_type='application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = requirement_form.errors
            return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        milestone = project_obj.milestones.all()
        return render(request, 'project/requirement.html', {'milestone': milestone})