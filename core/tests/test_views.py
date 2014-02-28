from django.test import TestCase
import core.models as models
from .base import LoggedTestCase, BaseModalTestCase

class GuestTest(TestCase):
    def test_index(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/account/login/?next=/')


class IndexTest(LoggedTestCase):
    def test_index_help_redirect(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/help/')

    def test_index_help_no_redirect(self):
        models.Application(name='testapp').save()
        response = self.client.get('/')
        self.assertContains(response, 'testapp')


class ApplicationTest(LoggedTestCase):
    fixtures = ['test_user', 'test_application']

    def test_application(self):
        response = self.client.get('/application/1/')
        self.assertContains(response, 'testapp')


class EnvironmentTest(LoggedTestCase):
    fixtures = ['test_user', 'test_application', 'test_environment']

    def test_environment(self):
        response = self.client.get('/environment/1/')
        self.assertContains(response, 'testenvironment')


class SettingsTest(LoggedTestCase):
    fixtures = ['test_user', 'test_application']

    def test_index(self):
        response = self.client.get('/settings/')
        self.assertContains(response, 'testapp')

    def test_applications(self):
        response = self.client.get('/settings/applications/')
        self.assertContains(response, 'testapp')

    def test_users(self):
        response = self.client.get('/settings/users/')
        self.assertContains(response, 'Test UserName')

    def test_roles(self):
        response = self.client.get('/settings/users/')
        self.assertContains(response, 'app')


class HelpTest(LoggedTestCase):
    def test_help(self):
        response = self.client.get('/help/')
        self.assertContains(response, 'Help')


class CoreModalServerroleTest(LoggedTestCase, BaseModalTestCase):
    @property
    def url(self):
        return '/modal_form/a:/serverrole/'

class CoreModalApplicationTest(LoggedTestCase, BaseModalTestCase):
    fixtures = ['test_user', 'test_application']
    @property
    def url(self):
        return '/modal_form/a:/application/'

class CoreModalEnvironmentTest(LoggedTestCase, BaseModalTestCase):
    fixtures = ['test_user', 'test_application', 'test_environment']
    @property
    def url(self):
        return '/modal_form/a:/environment/'