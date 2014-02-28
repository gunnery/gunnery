from django.test import TestCase
import core.models as models
from core.tests.base import LoggedTestCase, BaseModalTestCase

class GuestTest(TestCase):
    def test_login(self):
        response = self.client.get('/account/login/')
        self.assertContains(response, 'Please Sign In')


class AccountTest(LoggedTestCase):
    def test_settings(self):
        response = self.client.get('/account/settings/')
        self.assertContains(response, 'Account settings')

    def test_profile(self):
    	response = self.client.get('/account/profile/1/')
    	self.assertContains(response, 'Test UserName')


class CoreModalUserTest(LoggedTestCase, BaseModalTestCase):
    @property
    def url(self):
        return '/modal_form/a:account/user/'