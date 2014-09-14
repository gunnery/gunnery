from .base import LoggedTestCase
from core.tests.fixtures import *


class SettingsTest(LoggedTestCase):
    def test_user_profile(self):
        response = self.client.get('/settings/account/profile/')
        self.assertContains(response, 'Save')

    def test_user_password(self):
        response = self.client.get('/settings/account/password/')
        self.assertContains(response, 'Save')

    def test_user_notifications(self):
        response = self.client.get('/settings/account/notifications/')
        self.assertEqual(response.status_code, 200)
        application = ApplicationFactory(department=self.department)
        response = self.client.get('/settings/account/notifications/')
        self.assertContains(response, application.name)

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