from django import template
from piebase.models import Ticket,Comment,Requirement
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
