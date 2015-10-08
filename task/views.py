import json
from django.shortcuts import render, HttpResponse
from task.forms import TaskForm
from piebase.models import TicketStatus, Project, Role
from project.signals import create_timeline


def add_task(request, slug, milestone_slug):
    project_obj = Project.objects.get(slug=slug, organization=request.user.organization)
    if request.method == 'POST':
        add_task_dict = request.POST.copy()
        add_task_dict['project'] = project_obj.id
        json_data = {}
        add_task_form = TaskForm(add_task_dict, project=project_obj, user=request.user)
        if add_task_form.is_valid():
            json_data['error'] = False
            task = add_task_form.save()
            msg = "created " + task.name + " in requirement " + task.requirement.name + " of milestone " + task.milestone.name
            create_timeline.send(sender=request.user, content_object=task, namespace=msg,
                         event_type="task created", project=project_obj)
            msg = "task " + task.name + " is assigned to " + task.assigned_to.username
            create_timeline.send(sender=request.user, content_object=task.assigned_to, namespace=msg,
                         event_type="task assigned", project=project_obj)
            return HttpResponse(json.dumps(json_data), content_type='application/json')
        else:
            json_data['error'] = True
            json_data['form_errors'] = add_task_form.errors
            return HttpResponse(json.dumps(json_data), content_type='application/json')
    else:
        requirement_list = project_obj.requirements.filter(milestone__slug=milestone_slug)
        ticket_status_list = TicketStatus.objects.filter(project=project_obj).order_by('id')
        assigned_to_list = []
        for member in project_obj.members.all():
            try:
                Role.objects.get(users__email=member.email, project=project_obj)
                assigned_to_list.append(member)
            except:
                pass
        milestone = project_obj.milestones.get(slug=milestone_slug)
        return render(request, 'task/add_task.html',
                      {'requirement_list': requirement_list, 'ticket_status_list': ticket_status_list,
                       'assigned_to_list': assigned_to_list, 'slug': slug, 'milestone': milestone})
