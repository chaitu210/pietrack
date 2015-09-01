import json
from django.shortcuts import render, HttpResponse
from task.forms import TaskForm
from piebase.models import Milestone, Requirement, TicketStatus, User, Ticket, Project

def add_task(request, slug):
    project_obj = Project.objects.get(slug = slug)
    if request.method == 'POST':
        add_task_dict= request.POST.copy()
        add_task_dict['project'] = project_obj.id
        json_data = {}
        add_task_form = TaskForm(add_task_dict)
        if add_task_form.is_valid():
            json_data['error'] = False
            add_task_form.save()
            return HttpResponse(json.dumps(json_data), content_type = 'application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = add_task_form.errors
            return HttpResponse(json.dumps(json_data), content_type = 'application/json')
    else:
        requirement_list = project_obj.requirements.all()
        ticket_status_list = TicketStatus.objects.filter(project = project_obj)
        assigned_to_list = project_obj.members.all()
        return render(request, 'task/add_task.html', {'requirement_list': requirement_list, 'ticket_status_list': ticket_status_list, 'assigned_to_list': assigned_to_list})
