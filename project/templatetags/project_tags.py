import os
from django import template
from piebase.models import Ticket,Comment,Requirement,Role
from django.core.paginator import Paginator
register = template.Library()

@register.filter
def Task_list(status,milestone):
	tasks = Ticket.objects.filter(status=status,milestone=milestone)
	p = Paginator(tasks,10)
	return p.page(1)

@register.filter
def Requirement_Task_list(status,requirement_id):
	requirement = Requirement.objects.get(id=requirement_id)
	tasks = requirement.tasks.filter(status=status)
	p = Paginator(tasks,10)
	return p.page(1)

@register.filter
def count_comments(ticket):
	return Comment.objects.filter(ticket=ticket).count()

@register.filter
def Team_mem(task):
	return task.project.members.all()

@register.filter
def get_user_Role(user):
	try:
		return Role.objects.get(users=user)
	except Exception, e:
		return user.pietrack_role
	
@register.filter
def sub_comments(sub_comment):
	l=[]
	reply = sub_comment.comment_parent.all()
	if(reply):
		l.append(sub_comment)
		for sc in reply:
			l.extend(sub_comments(sc))
		return l
	return [sub_comment]

@register.filter
def level1comments(task):
	return Comment.objects.filter(ticket=task, parent=None)[::-1]

@register.filter
def filename(value):
	return os.path.basename(value.file.name)