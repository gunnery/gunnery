from django.test import TestCase
from guardian.shortcuts import get_objects_for_user
from unittest import skip

from .base import LoggedTestCase, BaseModalTestCase, BaseModalTests
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
        application = ApplicationFactory(department=self.department)
        response = self.client.get('/application/%d/' % application.id)
        self.assertContains(response, application.name)

    def test_application_forbidden(self):
        application = ApplicationFactory(department=DepartmentFactory())
        response = self.client.get('/application/%d/' % application.id)
        self.assertEqual(response.status_code, 302)


class EnvironmentTest(LoggedTestCase):
    def test_environment(self):
        application = ApplicationFactory(department=self.department)
        environment = EnvironmentFactory(application=application)
        response = self.client.get('/environment/%d/' % environment.id)
        self.assertContains(response, environment.name)

    def test_environment_forbidden(self):
        environment = EnvironmentFactory()
        response = self.client.get('/environment/%d/' % environment.id)
        self.assertEqual(response.status_code, 302)


class SettingsTest(LoggedTestCase):
    def test_user_profile(self):
        response = self.client.get('/settings/account/profile/')
        self.assertContains(response, 'Save')

    def test_user_password(self):
        response = self.client.get('/settings/account/password/')
        self.assertContains(response, 'Save')

    def test_user_notifications(self):
        response = self.client.get('/settings/account/notifications/')
        self.assertContains(response, 'Save')

    def test_user_notifications_save(self):
        application = ApplicationFactory(department=self.department)
        data = {'notification[%s]' % application.id: 1}
        response = self.client.post('/settings/account/notifications/', data)
        self.assertEqual(response.context['notifications'][application.id], True)

        data = {}
        response = self.client.post('/settings/account/notifications/', data)
        self.assertEqual(response.context['notifications'][application.id], False)

    def test_department_applications(self):
        response = self.client.get('/settings/department/applications/')
        self.assertEqual(response.status_code, 302)

    def test_department_users(self):
        response = self.client.get('/settings/department/users/')
        self.assertEqual(response.status_code, 302)

    def test_department_serverroles(self):
        response = self.client.get('/settings/department/serverroles/')
        self.assertEqual(response.status_code, 302)

    def test_system_departments(self):
        response = self.client.get('/settings/system/departments/')
        self.assertEqual(response.status_code, 302)

    def test_system_users(self):
        response = self.client.get('/settings/system/users/')
        self.assertEqual(response.status_code, 302)


class SettingsManagerTest(SettingsTest):
    logged_is_manager = True

    def test_department_applications(self):
        response = self.client.get('/settings/department/applications/')
        self.assertContains(response, 'No applications yet.')

        application = ApplicationFactory(department=self.department)
        response = self.client.get('/settings/department/applications/')
        self.assertContains(response, application.name)

    def test_department_users(self):
        response = self.client.get('/settings/department/users/')
        self.assertContains(response, 'Create')

    def test_department_serverroles(self):
        response = self.client.get('/settings/department/serverroles/')
        self.assertContains(response, 'No roles yet.')

        server_role = ServerRoleFactory(department=self.department)
        response = self.client.get('/settings/department/serverroles/')
        self.assertContains(response, server_role.name)


class SettingsSuperuserTest(SettingsManagerTest):
    logged_is_superuser = True

    def test_system_departments(self):
        response = self.client.get('/settings/system/departments/')
        self.assertContains(response, 'Create')

    def test_system_users(self):
        response = self.client.get('/settings/system/users/')
        self.assertContains(response, 'Create')


class HelpTest(LoggedTestCase):
    def test_help(self):
        response = self.client.get('/help/')
        self.assertContains(response, 'Help')


class CoreModalServerroleTest(BaseModalTestCase, BaseModalTests):
    url = '/modal_form/a:/serverrole/'
    object_factory = ServerRoleFactory


class CoreModalApplicationTest(BaseModalTestCase, BaseModalTests):
    url = '/modal_form/a:/application/'
    object_factory = ApplicationFactory


class CoreModalEnvironmentTest(BaseModalTestCase, BaseModalTests):
    url = '/modal_form/a:/environment/'
    object_factory = EnvironmentFactory


class DepartmentSwitcherTest(LoggedTestCase):
    # def test_switch_to_valid_department(self):
    #     response = self.client.get('/department/switch/%d/' % self.department.id)
    #     self.assertRedirects(response, '/')

    def test_switch_to_invalid_department(self):
        department = DepartmentFactory()
        response = self.client.get('/department/switch/%d/' % department.id)
        self.assertRedirects(response, '/account/login/?next=/department/switch/%d/' % department.id)
