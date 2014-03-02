from django.test import TestCase

class LoggedTestCase(TestCase):
    fixtures = ['test_user.json']

    def setUp(self):
        result = self.client.login(username='admin@test.com', password='testtest')
        self.assertTrue(result, 'Login failed')


class BaseModalTestCase(object):
    def test_create_form(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_edit_form(self):
        response = self.client.get('%s1/' % self.url)
        self.assertEquals(response.status_code, 200)

    def test_delete(self):
        response = self.client.post('%s1/' % self.url)
        self.assertEquals(response.status_code, 200)
