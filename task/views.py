import json
from django.shortcuts import render, HttpResponse
from task.forms import AddTaskForm
from piebase.models import Milestone, Requirement, TicketStatus, User, Ticket, Project

def add_task(request, slug):
    project_obj = Project.objects.get(slug = slug)
    if request.method == 'POST':
        add_task_dict= request.POST.copy()
        add_task_dict['project'] = project_obj.id
        try:
            print add_task_dict
            ticket_name = request.POST.get('name')
            if Ticket.objects.filter(name = ticket_name).exists():
                ticket_type = 'issue'
            else:
                ticket_type = 'enhancement'
            add_task_dict['ticket_type'] = ticket_type
        except:
            print 'hi'
        json_data = {}
        add_task_form = AddTaskForm(add_task_dict)
        if add_task_form.is_valid():
            #json_data['error'] = False
            #if Requirement.objects.filter(id = request.POST.get('requirement')).exists():
            #    Requirement.objects.get(id = request.POST.get('requirement'))
            #else:
            #    reuirement_obj = None
            #status_obj = TicketStatus.objects.get(id = request.POST.get('status'))
            #assigned_to_obj = User.objects.get(id = request.POST.get('assigned_to'))
            ##project_obj = requirement_obj.project
            #Ticket.objects.create(name = ticket_name, requirement = requirement_obj, status = status_obj, assigned_to = assigned_to_obj, finished_date = request.POST.get('finished_date'), description = request.POST.get('description'), project = project_obj, ticket_type = ticket_type)
            add_task_form.save()
            return HttpResponse(json.dumps(json_data), content_type = 'application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = add_task_form.errors
            return HttpResponse(json.dumps(json_data), content_type = 'application/json')
    else:
        requirement_list = [requirement for requirement in project_obj.requirements.all()]
        ticket_status_list = [ticket_status for ticket_status in TicketStatus.objects.all()]
        assigned_to_list = [assigned_to_user for assigned_to_user in project_obj.members.all()]
        return render(request, 'task/add_task.html', {'requirement_list': requirement_list, 'ticket_status_list': ticket_status_list, 'assigned_to_list': assigned_to_list})
