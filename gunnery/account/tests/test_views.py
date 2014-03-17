from django.test import TestCase

from core.tests.base import LoggedTestCase, BaseModalTestCase


class GuestTest(TestCase):
    def test_login(self):
        response = self.client.get('/account/login/')
        self.assertContains(response, 'Please Sign In')


class CoreModalUserTest(BaseModalTestCase):
    @property
    def url(self):
        return '/modal_form/a:account/user/'