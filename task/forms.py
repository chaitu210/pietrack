from django import forms
from piebase.models import Ticket

class TaskForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['name', 'milestone', 'requirement', 'status', 'finished_date', 'assigned_to', 'description', 'project', 'ticket_type']
