from django.test import TestCase


# Create your tests here.

class addtestcase(TestCase):
    def test_simple_addition(self):
        self.assertEquals(5, 3 + 2)
