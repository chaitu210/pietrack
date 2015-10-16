from django import template
from piebase.models import Ticket, Comment, Requirement, Role
from django.core.paginator import Paginator
from datetime import datetime

register = template.Library()


@register.filter
def Task_list(status, search_filter):
    milestone = search_filter[0]
    assigned_to = map(int,search_filter[1])
    requirements = map(int,search_filter[2])
    task_list = map(int,search_filter[3])
    start_date = search_filter[4]
    end_date = search_filter[5]
    tasks = Ticket.objects.filter(status=status, milestone=milestone)
    if requirements:
        tasks = tasks.filter(requirement__id__in=requirements)
    if assigned_to:
        tasks = tasks.filter(assigned_to__id__in=assigned_to)
    if task_list:
        tasks = tasks.filter(id__in=task_list)
    if start_date!='':
        try:
            start_date = datetime.strptime(start_date+u' 00:00:00', '%m/%d/%Y %H:%M:%S')
            tasks = tasks.filter(created_date__gte=start_date)
        except:
            pass
    if end_date!='':
        try:
            end_date = datetime.strptime(end_date+u' 00:00:00', '%m/%d/%Y %H:%M:%S')
            tasks = tasks.filter(created_date__lte=end_date)
        except:
            pass
    p = Paginator(tasks, 10)
    return p.page(1)


@register.filter
def Requirement_Task_list(status, requirement_id):
    requirement = Requirement.objects.get(id=requirement_id)
    tasks = requirement.tasks.filter(status=status)
    p = Paginator(tasks, 10)
    return p.page(1)


@register.filter
def count_comments(ticket):
    return Comment.objects.filter(ticket=ticket).count()


@register.filter
def Team_mem(task):
    return task.project.members.all()


@register.filter
def get_user_Role(user, project):
    try:
        return Role.objects.get(users=user, project=project)
    except Exception, e:
        return user.pietrack_role


@register.filter
def is_project_admin(user, slug):
    try:
        return Role.objects.get(users=user, project__slug=slug,
                                project__organization=user.organization).is_project_admin
    except:
        return False


@register.filter
def sub_comments(sub_comment):
    l = []
    reply = sub_comment.comment_parent.all()
    if (reply):
        l.append(sub_comment)
        for sc in reply:
            l.extend(sub_comments(sc))
        return l
    return [sub_comment]


@register.filter
def level1comments(task):
    return Comment.objects.filter(ticket=task, parent=None)[::-1]


@register.filter
def milestone_requirements(milestone):
    return Requirement.objects.filter(milestone=milestone)
