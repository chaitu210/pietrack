import json, random, string
from django.shortcuts import render
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
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
                    #send_mail('Subject here', 'Here is the message.', 'dineshmcmf@gmail.com', [email])
                    pass
                else:
                    random_password = ''.join(random.choice(string.digits) for _ in xrange(8))
                    User.objects.create(email = email, username = email, password = random_password, organization = organization_obj, pietrack_role = 'user')
                    #send_mail('Subject here', 'Here is the message.', 'dineshmcmf@gmail.com', [email])
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
