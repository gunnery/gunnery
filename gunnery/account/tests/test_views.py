from django.test import TestCase


class GuestTest(TestCase):
    def test_login(self):
        response = self.client.get('/account/login/')
        self.assertContains(response, 'Please Sign In')

