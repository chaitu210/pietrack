from django import forms
from piebase.models import Ticket
from django.template.defaultfilters import slugify


class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)
        self.milestone = kwargs.pop('milestone', None)
        super(TaskForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Ticket
        fields = ['name', 'status', 'finished_date',
                  'assigned_to', 'description', 'ticket_type']

    def save(self, commit=True):
        task = super(TaskForm, self).save(commit=False)
        if self.instance:
            task = self.instance
        task.project = self.project
        task.slug = slugify(self.cleaned_data.get('name'))
        task.milestone = self.milestone
        task.created_by = self.user
        task.ticket_type = 'task'
        if commit:
            task.save()
        return task
