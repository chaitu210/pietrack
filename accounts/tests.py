from django.test import TestCase
from piebase.models import User

class TestUser(TestCase):
    def setup(self):
        pass

    def test_register(self):
        response = self.client.post('/accounts/register/', {'email': 'c@c.com', 'first_name': 'cc', 'password': 'dinesh', 'confirm_password': 'dinesh', 'username': 'cc', 'organization': 'c_org'})
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.client.post('/accounts/login/', {'email': 'c@c.com', 'password': 'dinesh'})
        self.assertEqual(response.status_code, 200)

    def test_forgot_password(self):
        response = self.client.post('/accounts/forgot_password/', {'email': 'c@c.com'})
        self.assertEqual(response.status_code, 200)

