from django.test import TestCase

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


class HelpTest(LoggedTestCase):
    def test_help(self):
        response = self.client.get('/help/')
        self.assertContains(response, 'Help')


class CoreModalServerroleTest(BaseModalTestCase, BaseModalTests):
    url_name = 'modal_form'
    url_params = {'form_name': 'serverrole'}
    object_factory = ServerRoleFactory

    def test_create(self):
        response, obj = self._test_create({'name': 'ServerRoleName'})
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})

    def test_edit(self):
        obj = self.object_factory(department=self.department)
        data = {'name': 'ServerRoleName2'}
        response, obj_updated = self._test_edit(obj, data)
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})
        self.assertEqual(obj_updated.name, 'ServerRoleName2')


class CoreModalApplicationTest(BaseModalTestCase, BaseModalTests):
    url_name = 'modal_form'
    url_params = {'form_name': 'application'}
    object_factory = ApplicationFactory

    def test_create(self):
        response, obj = self._test_create({'name': 'ApplicationName'})
        self.assertJSONEqual(response.content,
                             {"status": True,
                              "action": "redirect",
                              "target": reverse('application_page', kwargs={'application_id': obj.id})})

    def test_edit(self):
        obj = self.object_factory(department=self.department)
        data = {'name': 'ApplicationName2'}
        response, obj_updated = self._test_edit(obj, data)
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})
        self.assertEqual(obj_updated.name, 'ApplicationName2')


class CoreModalEnvironmentTest(BaseModalTestCase, BaseModalTests):
    url_name = 'modal_form'
    url_params = {'form_name': 'environment', 'parent_name': 'application'}
    object_factory = EnvironmentFactory

    @classmethod
    def setUpClass(cls):
        super(CoreModalEnvironmentTest, cls).setUpClass()
        cls.application = ApplicationFactory(department=cls.department)
        cls.url_params['parent_id'] = cls.application.id

    def test_create(self):
        response, obj = self._test_create({'name': 'EnvironmentName', 'description': '123',
                                           'application': self.application.id})
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})

    def test_edit(self):
        application = ApplicationFactory(department=self.department)
        obj = self.object_factory(application=application)
        data = {'name': 'EnvironmentName2', 'application': self.application.id}
        response, obj_updated = self._test_edit(obj, data)
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})
        self.assertEqual(obj_updated.name, 'EnvironmentName2')


class DepartmentSwitcherTest(LoggedTestCase):
    # def test_switch_to_valid_department(self):
    #     response = self.client.get('/department/switch/%d/' % self.department.id)
    #     self.assertRedirects(response, '/')

    def test_switch_to_invalid_department(self):
        department = DepartmentFactory()
        response = self.client.get('/department/switch/%d/' % department.id)
        self.assertRedirects(response, '/account/login/?next=/department/switch/%d/' % department.id)
