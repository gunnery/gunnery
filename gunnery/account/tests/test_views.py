from django.test import TestCase
from account.tests.fixtures import UserFactory

from core.tests.base import LoggedTestCase, BaseModalTestCase, BaseModalTests


class GuestTest(TestCase):
    def test_login(self):
        response = self.client.get('/account/login/')
        self.assertContains(response, 'Please Sign In')


class CoreModalUserTest(BaseModalTestCase, BaseModalTests):
    object_factory = UserFactory

    @property
    def url(self):
        return '/modal_form/a:account/user/'