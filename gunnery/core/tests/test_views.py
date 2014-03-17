from django.test import TestCase

from .base import LoggedTestCase, BaseModalTestCase
from core.tests.fixtures import *


class GuestTest(TestCase):
    def test_index(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/account/login/?next=/')


class IndexTest(LoggedTestCase):
    def test_index_help_redirect(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/help/')

    def test_index_help_no_redirect(self):
        application = ApplicationFactory(department=self.department)
        response = self.client.get('/')
        self.assertContains(response, application.name)


class ApplicationTest(LoggedTestCase):
    def test_application(self):
        application = ApplicationFactory()
        response = self.client.get('/application/%d/' % application.id)
        self.assertContains(response, application.name)


class EnvironmentTest(LoggedTestCase):
    def test_environment(self):
        environment = EnvironmentFactory()
        response = self.client.get('/environment/%d/' % environment.id)
        self.assertContains(response, environment.name)


class SettingsTest(LoggedTestCase):
    def test_user_profile(self):
        response = self.client.get('/settings/user/profile/')
        self.assertContains(response, 'Save')

    def test_user_password(self):
        response = self.client.get('/settings/user/password/')
        self.assertContains(response, 'Save')

    def test_department_applications(self):
        application = ApplicationFactory(department=self.department)
        response = self.client.get('/settings/department/applications/')
        self.assertContains(response, application.name)

    def test_department_applications_empty(self):
        response = self.client.get('/settings/department/applications/')
        self.assertContains(response, 'No applications yet.')

    def test_department_users(self):
        response = self.client.get('/settings/department/users/')
        self.assertContains(response, 'Create')

    def test_department_serverroles(self):
        server_role = ServerRoleFactory(department=self.department)
        response = self.client.get('/settings/department/serverroles/')
        self.assertContains(response, server_role.name)

    def test_department_serverroles_empty(self):
        response = self.client.get('/settings/department/serverroles/')
        self.assertContains(response, 'No roles yet.')

    def test_system_departments(self):
        response = self.client.get('/settings/system/departments/')
        self.assertContains(response, 'Create')

    def test_system_users(self):
        response = self.client.get('/settings/system/users/')
        self.assertContains(response, 'Create')


class SettingsNotStaffTest(LoggedTestCase):
    logged_is_staff = False

    def test_system_departments(self):
        response = self.client.get('/settings/system/departments/')
        self.assertEqual(response.status_code, 302)

    def test_system_users(self):
        response = self.client.get('/settings/system/users/')
        self.assertEqual(response.status_code, 302)


class HelpTest(LoggedTestCase):
    def test_help(self):
        response = self.client.get('/help/')
        self.assertContains(response, 'Help')


class CoreModalServerroleTest(BaseModalTestCase):
    url = '/modal_form/a:/serverrole/'
    object_factory = ServerRoleFactory


class CoreModalApplicationTest(BaseModalTestCase):
    url = '/modal_form/a:/application/'
    object_factory = ApplicationFactory


class CoreModalEnvironmentTest(BaseModalTestCase):
    url = '/modal_form/a:/environment/'
    object_factory = EnvironmentFactory


class DepartmentSwitcherTest(LoggedTestCase):
    def test_switch_to_valid_department(self):
        pass

    def test_switch_to_invalid_department(self):
        pass