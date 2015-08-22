from django import forms
from piebase.models import Project,Organization, User


class CreateProjectForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		self.organization = kwargs.pop('organization', None)
		super(CreateProjectForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Project
		fields = ['name','description']

	def clean_name(self):
		name = self.cleaned_data['name']
		if(Project.objects.filter(name=name,organization=self.organization)):
			raise forms.ValidationError('Project with this name already exists.')
		return name 

class CreateMemberForm(forms.Form):
    email = forms.EmailField()
    designation = forms.CharField()
    description = forms.Textarea()
