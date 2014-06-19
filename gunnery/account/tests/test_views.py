from django.test import TestCase
from account.tests.fixtures import UserFactory

from core.tests.base import BaseModalTestCase, BaseModalTests


class GuestTest(TestCase):
    def test_login(self):
        response = self.client.get('/account/login/')
        self.assertContains(response, 'Please Sign In')


class CoreModalUserTest(BaseModalTestCase, BaseModalTests):
    url_name = 'modal_form'
    url_params = {'app': 'account', 'form_name': 'user'}
    object_factory = UserFactory

    def test_create(self):
        response, obj = self._test_create({'email': 'test@test.com', 'password': 'password', 'name': 'test test'})
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})

    def test_edit(self):
        obj = self.object_factory()
        data = {'email': 'test2@test.com', 'password': 'password', 'name': 'test2 test2'}
        response, obj_updated = self._test_edit(obj, data)
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})
        self.assertEqual(obj_updated.name, 'test2 test2')

    def get_created_object(self, data):
        del data['password']
        return super(CoreModalUserTest, self).get_created_object(data)