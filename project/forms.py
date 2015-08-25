from django import forms
from piebase.models import Project,Priority,Severity,Organization,User,TicketStatus
from django.template.defaultfilters import slugify


class CreateProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization', None)
        super(CreateProjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Project
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data['name']
        if (Project.objects.filter(name=name, organization=self.organization)):
            raise forms.ValidationError('Project with this name already exists.')
        return name


class PriorityIssueForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.project = kwargs.pop('project', None)
		super(PriorityIssueForm, self).__init__(*args, **kwargs)
	
	class Meta:
		model = Priority
		fields = ['name','color']

	def clean_name(self):
		name = self.cleaned_data['name']
		project = Project.objects.get(slug=self.project);
		if(Priority.objects.filter(name=name,project=project)):
			raise forms.ValidationError('Priority with this name already exists')
		return name

class PriorityIssueFormEdit(forms.ModelForm):

	class Meta:
		model = Priority
		fields = ['name','color']

class SeverityIssueForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.project = kwargs.pop('project', None)
		super(SeverityIssueForm, self).__init__(*args, **kwargs)
	
	class Meta:
		model = Severity
		fields = ['name','color']

	def clean_name(self):
		name = self.cleaned_data['name']
		project = Project.objects.get(slug=self.project);
		if(Priority.objects.filter(name=name,project=project)):
			raise forms.ValidationError('Severity with this name already exists')
		return name

class SeverityIssueFormEdit(forms.ModelForm):

	class Meta:
		model = Severity
		fields = ['name','color']

class TicketStatusForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.project = kwargs.pop('project', None)
		super(TicketStatusForm, self).__init__(*args, **kwargs)
	
	class Meta:
		model = TicketStatus
		fields = ['name','color']

	def clean_name(self):
		name = self.cleaned_data['name']
		project = Project.objects.get(slug=self.project);
		if(Priority.objects.filter(name=name,project=project)):
			raise forms.ValidationError('Severity with this name already exists')
		return name

class TicketStatusFormEdit(forms.ModelForm):

	class Meta:
		model = TicketStatus
		fields = ['name','color']		

class CreateMemberForm(forms.Form):
    email = forms.EmailField()
    designation = forms.CharField()
    description = forms.Textarea()
