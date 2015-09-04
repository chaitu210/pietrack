from django import template
from piebase.models import Ticket,Comment
from django.core.paginator import Paginator
register = template.Library()

@register.filter
def Task_list(status,milestone):
	tasks = Ticket.objects.filter(status=status,milestone=milestone)
	p = Paginator(tasks,10)
	return p.page(1)

@register.filter
def count_comments(ticket):
	return Comment.objects.filter(ticket=ticket).count()