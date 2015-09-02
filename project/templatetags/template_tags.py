from django import template
from piebase.models import Ticket,Comment

register = template.Library()

@register.filter
def Task_list(status,project):
    return Ticket.objects.filter(status=status,project=project)

@register.filter
def count_comments(ticket):
	return Comment.objects.filter(ticket=ticket).count()
