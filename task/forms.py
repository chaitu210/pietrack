from django import forms
from piebase.models import Ticket

class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)


    class Meta:
        model = Ticket
        fields = ['name', 'milestone', 'requirement', 'status', 'finished_date', 'assigned_to', 'description', 'project', 'ticket_type']

        
    def save(self):
        task = super(TaskForm, self).save(commit=False)
        task.slug = self.cleaned_data.get('name')
        task.save()
