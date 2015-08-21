import json, random, string
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from piebase.models import User, Project, Organization, Role
from forms import CreateProjectForm, CreateMemberForm


@login_required
def create_project(request):
    print 'oooooooooooooooooooooo'
    template_name = 'create_project.html'
    if(request.method=="POST"):     
        print '((((((((((((((((((((((((((((((('
        organization=request.user.organization
        form = CreateProjectForm(request.POST,organization=organization)
        if(form.is_valid()):
            print 'validdddddddddddddddddddddddddddd'
            slug = slugify(request.POST['name'])
            project_obj = Project.objects.create(name=request.POST['name'],slug=slug,description=request.POST['description'],modified_date=timezone.now(),organization=organization)
            project_id = project_obj.id
            json_data = {'error':False,'errors':form.errors, 'project_id': project_id}
            return HttpResponse(json.dumps(json_data), content_type="application/json")
        else:
            json_data = {'error':True,'errors':form.errors}
            return HttpResponse(json.dumps(json_data), content_type="application/json")
    return render(request,template_name) 


@login_required
def list_of_projects(request):
    template_name = 'list_of_projects.html'
    projects_list=Project.objects.all()
    user_objects=User.objects.all()
    dict_items={'projects_list':projects_list, 'user_objects':user_objects}
    return render(request, template_name, dict_items)

@login_required
@csrf_exempt
def create_member(request, project_id):
    print request.POST
    if request.method == 'POST':
        json_data = {}
        json_post_index = 0
        email_list = request.POST.getlist('email')
        designation_list = request.POST.getlist('designation')
        description = request.POST.get('description')
        post_dict = {'description': description}
        post_tuple = zip(email_list, designation_list)
        print post_tuple
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
                    #pass
                    print 'from existing'
                else:
                    random_password = ''.join(random.choice(string.digits) for _ in xrange(8))
                    #print organization_obj.name
                    User.objects.create(email = email, username = email, password = random_password, organization = organization_obj, pietrack_role = 'user')
                    #send_mail('Subject here', 'Here is the message.', 'dineshmcmf@gmail.com', [email])
                    #pass
                    #print 'not exist'
                project_obj = Project.objects.get(id = project_id)
                user_obj = User.objects.get(email = email)
                project_obj.members.add(user_obj)
                project_obj.organization = organization_obj
                project_obj.save()

                role_obj = Role.objects.create(name = designation, project = project_obj)
                role_obj.users.add(user_obj)
                role_obj.save()
                json_data['error'] = False
                #return HttpResponse(json.dumps(json_data), content_type = 'application/json')
            else:
                print 'from invalid'
                json_data['error'] = True #, 'errors': create_member_form.errors, 'json_post_index': json_post_index}
            json_data[json_post_index] = create_member_form.errors
            json_post_index += 1
            #print '---------------------------------'
            #print json_data
            #print '---------------------------------'
        return HttpResponse(json.dumps(json_data), content_type = 'application/json')
    else:
        print 'from get'
        return render(request, 'create_member.html')


