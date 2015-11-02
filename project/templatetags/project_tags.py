from django import template
from piebase.models import Ticket, Comment, Role
 # Requirement,
from django.core.paginator import Paginator
from datetime import datetime
from django.db.models import Q

register = template.Library()


@register.filter
def Task_list(status, search_filter):
    milestone = search_filter[0]
    assigned_to = map(int, search_filter[1])
    task_list = map(int, search_filter[2])
    start_date = search_filter[3]
    end_date = search_filter[4]
    tasks = Ticket.objects.filter(status=status, milestone=milestone)
    if assigned_to:
        tasks = tasks.filter(assigned_to__id__in=assigned_to)
    if task_list:
        tasks = tasks.filter(id__in=task_list)
    if start_date != '':
        try:
            start_date = datetime.strptime(start_date + u' 00:00:00', '%m/%d/%Y %H:%M:%S')
            tasks = tasks.filter(created_date__gte=start_date)
        except:
            pass
    if end_date != '':
        try:
            end_date = datetime.strptime(end_date + u' 23:59:59', '%m/%d/%Y %H:%M:%S')
            tasks = tasks.filter(finished_date__lte=end_date)
        except:
            pass
    p = Paginator(tasks, 10)
    return p.page(1)


@register.filter
def issue_list(search_filter):
    assigned_to = map(int, search_filter[0])
    issue_type = search_filter[1]
    issue = map(int, search_filter[2])
    start_date = search_filter[3]
    end_date = search_filter[4]
    issues = Ticket.objects.filter(~Q(ticket_type='task'))
    if assigned_to:
        issues = issues.filter(assigned_to__id__in=assigned_to)

    if issue_type:
        issues = issues.filter(ticket_type__in=issue_type)

    if issue:
        issues = issues.filter(id__in=issue)

    if start_date != '':
        try:
            start_date = datetime.strptime(start_date + u' 00:00:00', '%m/%d/%Y %H:%M:%S')
            issues = issues.filter(created_date__gte=start_date)
        except:
            pass
    if end_date != '':
        try:
            end_date = datetime.strptime(end_date + u' 23:59:59', '%m/%d/%Y %H:%M:%S')
            issues = issues.filter(finished_date__lte=end_date)
        except:
            pass

    return issues


@register.filter
def count_comments(ticket):
    return Comment.objects.filter(ticket=ticket).count()


@register.filter
def Team_mem(task):
    return task.project.members.all()


@register.filter
def get_user_Role(user, project):
    try:
        if user.pietrack_role=='admin':
            return "Organization Admin"
        return Role.objects.get(users=user, project=project)
    except Exception, e:
        return user.pietrack_role


@register.filter
def is_project_admin(user, slug):
    try:
        if user.pietrack_role == 'admin':
            return True
        elif user.projects.get(slug=slug).admins.filter(id=user.id):
            return True
        return False
    except:
        return False


@register.filter
def sub_comments(sub_comment):
    l = []
    reply = sub_comment.comment_parent.all()
    if reply:
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
    return Ticket.objects.filter(milestone=milestone)
