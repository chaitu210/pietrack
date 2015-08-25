from django.test import TestCase
from piebase.models import User, Organization, Project

class TestUser(TestCase):
    def setup(self):
        self.organization_obj = Organization.objects.create(name = 'ee_org')
        User.objects.create_user(username = 'e@e.com', email = 'e@e.com', password = 'dinesh', full_name = 'ee', organization = self.organization_obj)

    def test_create_project(self):
        self.client.login(username = 'e@e.com', password = 'dinesh')
        response = self.client.post('/project/create_project', {'name': 'ee_proj', 'description': 'fusssss'})
        self.assertEqual(response.status_code, 301)
