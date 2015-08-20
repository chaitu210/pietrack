from django.shortcuts import render
from django.http import HttpResponse
from piebase.models import Project,Organization
from forms import CreateProjectForm
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from piebase.models import Project, User
import json


@login_required
def create_project(request):
	template_name = 'create_project.html'
	if(request.method=="POST"):
		organization=request.user.organization
		form = CreateProjectForm(request.POST,organization=organization)
		if(form.is_valid()):
			slug = slugify(request.POST['name'])
			Project.objects.create(name=request.POST['name'],slug=slug,description=request.POST['description'],modified_date=timezone.now(),organization=organization)
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
