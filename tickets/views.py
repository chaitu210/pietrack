import json
from django.shortcuts import render, HttpResponse
from tickets.forms import AddTaskForm
from piebase.models import Milestone, Requirement, TicketStatus, User, Ticket

def add_task(request):
    if request.method == 'POST':
        json_data = {}
        add_task_form = AddTaskForm(request.POST)
        if add_task_form.is_valid():
            ticket_name = request.POST.get('name')
            if Ticket.objects.filter(name = ticket_name).exists():
                ticket_type = 'issue'
            else:
                ticket_type = 'enhancement'
            json_data['error'] = False
            requirement_obj = Requirement.objects.get(id = request.POST.get('requirement'))
            status_obj = TicketStatus.objects.get(id = request.POST.get('status'))
            assigned_to_obj = User.objects.get(id = request.POST.get('assigned_to'))
            project_obj = requirement_obj.project
            Ticket.objects.create(name = ticket_name, requirement = requirement_obj, status = status_obj, assigned_to = assigned_to_obj, finished_date = request.POST.get('finished_date'), description = request.POST.get('description'), project = project_obj, ticket_type = ticket_type)
            return HttpResponse(json.dumps(json_data), content_type = 'application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = add_task_form.errors
            return HttpResponse(json.dumps(json_data), content_type = 'application/json')
    else:
        requirement_list = [requirement for requirement in Requirement.objects.all()]
        ticket_status_list = [ticket_status for ticket_status in TicketStatus.objects.all()]
        assigned_to_list = [assigned_to_user for assigned_to_user in User.objects.all()]
        return render(request, 'ticket/add_task.html', {'requirement_list': requirement_list, 'ticket_status_list': ticket_status_list, 'assigned_to_list': assigned_to_list})
