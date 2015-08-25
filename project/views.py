from django.shortcuts import render,redirect
from piebase.models import Project,Priority
from forms import CreateProjectForm,PriorityIssueForm,PriorityIssueFormEdit
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from piebase.models import Project, User
import json


@login_required
def create_project(request):
	print request.user
	template_name = 'create_project.html'
	if(request.method=="POST"):
		organization=request.user.organization
		form = CreateProjectForm(request.POST,organization=organization)
		if(form.is_valid()):
			slug = slugify(request.POST['name'])
			project = Project.objects.create(name=request.POST['name'],slug=slug,description=request.POST['description'],modified_date=timezone.now(),organization=organization)
			project.members.add(request.user)
			project.save()
			return HttpResponse(json.dumps({'error':False,'errors':form.errors}), content_type="application/json")
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
			print request.POST
			priority = Priority.objects.get(id=request.POST['old_id'],project=Project.objects.get(slug=slug));
			print  priority.color,priority.name
			priority.color = request.POST['color']
			priority.name = request.POST['name']
			priority.save()
			print  priority.color,priority.name
			return HttpResponse(json.dumps({'error':False,'color':request.POST['color'],'name':request.POST['name'],'id':request.POST['old_id']}),content_type="application/json")
		else:
			return HttpResponse(json.dumps({'error':True,'errors':form.errors}),content_type="application/json");	

def issues_priorities_delete(request,slug):
	Priority.objects.get(name=request.POST['name'],color=request.POST['color'],project=Project.objects.get(slug=slug)).delete();
	return HttpResponse(json.dumps({'error':False}),content_type="application/json");
