from django.test import TestCase

class LoggedTestCase(TestCase):
    fixtures = ['test_user']

    def setUp(self):
        result = self.client.login(username='admin@test.com', password='test')
        self.assertTrue(result, 'Login failed')