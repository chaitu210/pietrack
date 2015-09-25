from django import forms
from piebase.models import Ticket, Requirement


class TaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Ticket
        fields = ['name', 'requirement', 'status', 'finished_date',
                  'assigned_to', 'description', 'project', 'ticket_type']

    def save(self):
        task = super(TaskForm, self).save(commit=False)
        task.slug = self.cleaned_data.get('name')
        task.milestone = self.cleaned_data.get('requirement').milestone
        task.created_by = self.user
        task.save()
