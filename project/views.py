from django.shortcuts import render,redirect
from piebase.models import Project,Priority,Severity,TicketStatus
from forms import CreateProjectForm,PriorityIssueForm,PriorityIssueFormEdit,SeverityIssueForm,SeverityIssueFormEdit,TicketStatusForm,TicketStatusFormEdit
import json, random, string
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from piebase.models import User, Project, Organization, Role
from forms import CreateProjectForm, CreateMemberForm


@login_required
def create_project(request):
    template_name = 'create_project.html'
    if(request.method=="POST"):
        organization=request.user.organization
        form = CreateProjectForm(request.POST,organization=organization)
        if(form.is_valid()):
            slug = slugify(request.POST['name'])
            project_obj = Project.objects.create(name=request.POST['name'],slug=slug,description=request.POST['description'],modified_date=timezone.now(),organization=organization)
            project_id = project_obj.id
            json_data = {'error':False,'errors':form.errors, 'project_id': project_id}
            return HttpResponse(json.dumps(json_data), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error':True,'errors':form.errors}), content_type="application/json")
    return render(request,template_name)

@login_required
def list_of_projects(request):
    template_name = 'list_of_projects.html'
    projects_list=Project.objects.filter(members__email=request.user)
    dict_items={'projects_list':projects_list}
    return render(request, template_name, dict_items)

@login_required
def project_description(request, pk):
	template_name='project_description.html'
	project_object=Project.objects.filter(id=pk)
	project_members=project_object[0].members.all()
	dict_items={'project_object':project_object[0], 'project_members':project_members}
	return render(request, template_name, dict_items)

def project_details(request,slug):
	# print slug
	project = Project.objects.get(slug=slug)
	dictionary = {'project':project}
	template_name = 'Project-Project_Details.html'

	if(request.method=='POST'):
		print request.POST['oldname']
		organization=request.user.organization
		form = CreateProjectForm(request.POST,organization=organization)

		if(form.is_valid()):
			slug = slugify(request.POST['name'])
			project = Project.objects.get(slug=request.POST['oldname'],organization=organization)
			project.name=request.POST['name']
			project.slug = slug
			project.modified_date = timezone.now()
			project.save()
			return HttpResponse(json.dumps({'error':False,'slug':slug}), content_type="application/json")
		else:
			return HttpResponse(json.dumps({'error':True,'errors':form.errors}), content_type="application/json")

	return render(request, template_name, dictionary)


def delete_project(request,id):
	Project.objects.get(id=id).delete()
	return redirect("project:list_of_projects")


def issues_priorities(request,slug):
	template_name = 'issues-proities.html'
	if(request.method=='POST'):
		form = PriorityIssueForm(request.POST,project=slug)
		if(form.is_valid()):
			project = Priority.objects.create(name=request.POST['name'],color=request.POST['color'],project=Project.objects.get(slug=slug));
			return HttpResponse(json.dumps({'error':False,'color':request.POST['color'],'name':request.POST['name'],'proj_id':project.id}),content_type="application/json")
		else:
			return HttpResponse(json.dumps({'error':True,'errors':form.errors}),content_type="application/json");
	priority_list=Priority.objects.filter(project=Project.objects.get(slug=slug))
	return render(request,template_name,{'slug':slug,'priority_list':priority_list})

def issues_priorities_edit(request,slug):
	if(request.method=='POST'):
		form = PriorityIssueFormEdit(request.POST)
		if(form.is_valid()):
			priority = Priority.objects.get(id=request.POST['old_id'],project=Project.objects.get(slug=slug));
			priority.color = request.POST['color']
			priority.name = request.POST['name']
			priority.save()
			return HttpResponse(json.dumps({'error':False,'color':request.POST['color'],'name':request.POST['name'],'id':request.POST['old_id']}),content_type="application/json")
		else:
			return HttpResponse(json.dumps({'error':True,'errors':form.errors}),content_type="application/json");	

def issues_priorities_delete(request,slug):
	Priority.objects.get(name=request.POST['name'],color=request.POST['color'],project=Project.objects.get(slug=slug)).delete();
	return HttpResponse(json.dumps({'error':False}),content_type="application/json");

def issues_severities(request,slug):
    template_name = 'severities.html'
    if(request.method=='POST'):
        form = SeverityIssueForm(request.POST,project=slug)
        if(form.is_valid()):
            project = Severity.objects.create(name=request.POST['name'],color=request.POST['color'],project=Project.objects.get(slug=slug));
            return HttpResponse(json.dumps({'error':False,'color':request.POST['color'],'name':request.POST['name'],'proj_id':project.id}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error':True,'errors':form.errors}),content_type="application/json");
    priority_list=Severity.objects.filter(project=Project.objects.get(slug=slug))
    return render(request,template_name,{'slug':slug,'priority_list':priority_list})

def issues_severities_edit(request,slug):
    if(request.method=='POST'):
        form = SeverityIssueFormEdit(request.POST)
        if(form.is_valid()):
            priority = Severity.objects.get(id=request.POST['old_id'],project=Project.objects.get(slug=slug));
            priority.color = request.POST['color']
            priority.name = request.POST['name']
            priority.save()
            return HttpResponse(json.dumps({'error':False,'color':request.POST['color'],'name':request.POST['name'],'id':request.POST['old_id']}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error':True,'errors':form.errors}),content_type="application/json");   

def issues_severities_delete(request,slug):
    Severity.objects.get(name=request.POST['name'],color=request.POST['color'],project=Project.objects.get(slug=slug)).delete();
    return HttpResponse(json.dumps({'error':False}),content_type="application/json");

def ticket_status(request,slug):
    template_name = 'Attributes_Status.html'
    if(request.method=='POST'):
        print "before form" 
        form = TicketStatusForm(request.POST,project=slug)
        print "after form" 
        print form
        if(form.is_valid()):
            print "no error"
            tslug = slugify(request.POST['name'])
            project = TicketStatus.objects.create(name=request.POST['name'],slug=tslug,color=request.POST['color'],project=Project.objects.get(slug=slug));
            return HttpResponse(json.dumps({'error':False,'color':request.POST['color'],'name':request.POST['name'],'proj_id':project.id}),content_type="application/json")
        else:
            print "errors"
            return HttpResponse(json.dumps({'error':True,'errors':form.errors}),content_type="application/json");
    priority_list=TicketStatus.objects.filter(project=Project.objects.get(slug=slug))
    return render(request,template_name,{'slug':slug,'priority_list':priority_list})

def ticket_status_edit(request,slug):
    if(request.method=='POST'):
        form = TicketStatusFormEdit(request.POST)
        if(form.is_valid()):
            priority = TicketStatus.objects.get(id=request.POST['old_id'],project=Project.objects.get(slug=slug));
            priority.color = request.POST['color']
            priority.name = request.POST['name']
            priority.slug = slugify(request.POST['name']) 
            priority.save()
            return HttpResponse(json.dumps({'error':False,'color':request.POST['color'],'name':request.POST['name'],'id':request.POST['old_id']}),content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error':True,'errors':form.errors}),content_type="application/json");   

def ticket_status_delete(request,slug):
    TicketStatus.objects.get(name=request.POST['name'],color=request.POST['color'],project=Project.objects.get(slug=slug)).delete();
    return HttpResponse(json.dumps({'error':False}),content_type="application/json");




@login_required
def create_member(request, project_id):
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
                if User.objects.filter(email = email).exists():
                    send_mail('invitaition for project', 'time to code', 'dineshmcmf@gmail.com', [email])
                    pass
                else:
                    random_password = ''.join(random.choice(string.digits) for _ in xrange(8))
                    new_user_obj = User.objects.create(email = email, username = email, password = random_password, organization = organization_obj, pietrack_role = 'user')
                    change_password_link = '127.0.0.1:8000/accounts/change_password/' + str(new_user_obj.id) + '/'
                    send_mail('Invitation for project', 'time to code, before that change your password: ' + change_password_link, 'dineshmcmf@gmail.com', [email])
                project_obj = Project.objects.get(id = project_id)
                user_obj = User.objects.get(email = email)
                project_obj.members.add(user_obj)
                project_obj.organization = organization_obj
                project_obj.save()

                slug = ''.join(random.choice(string.ascii_letters + string.digits) for _ in xrange(10))
                role_obj = Role.objects.create(name = designation, slug = slug, project = project_obj)
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
        return HttpResponse(json.dumps(json_data), content_type = 'application/json')
    else:
        return render(request, 'create_member.html')
