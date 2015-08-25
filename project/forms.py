from django import forms
from piebase.models import Project,Priority,Organization,User
from django.template.defaultfilters import slugify



class CreateProjectForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		self.organization = kwargs.pop('organization', None)
		super(CreateProjectForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Project
		fields = ['name','description']

	def clean_name(self):
		name = self.cleaned_data['name']
		slug = slugify(name)
		print slug
		if(Project.objects.filter(organization=self.organization, slug=slug)):
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

class CreateMemberForm(forms.Form):
    email = forms.EmailField()
    designation = forms.CharField()
    description = forms.Textarea()
