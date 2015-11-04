from django import forms
from piebase.models import Ticket
from django.template.defaultfilters import slugify


class TaskForm(forms.ModelForm):

    finished_date = forms.DateField(required=True)
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)
        super(TaskForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Ticket
        fields = ['name', 'milestone', 'status', 'finished_date',
                  'assigned_to', 'description', 'ticket_type']

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance:
            existing_slug = self.instance.slug
        if self.project.project_tickets.filter(slug=slugify(name), ticket_type="task") and existing_slug!=slugify(name):
            raise forms.ValidationError("Task with this name already exists.")
        return name

    def save(self, commit=True):
        task = super(TaskForm, self).save(commit=False)
        if self.instance:
            task = self.instance
        task.project = self.project
        task.slug = slugify(self.cleaned_data.get('name'))
        task.created_by = self.user
        task.ticket_type = 'task'
        if commit:
            task.save()
        return task
