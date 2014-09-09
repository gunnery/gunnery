from django.test import TestCase

from .base import LoggedTestCase
from core.tests.fixtures import *
from task.tests.fixtures import TaskFactory, ExecutionFactory


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
        environment = EnvironmentFactory(application=application)
        task = TaskFactory(application=application)
        ExecutionFactory(task=task, environment=environment, user=self.user)
        response = self.client.get('/')
        self.assertContains(response, application.name)


class ApplicationTest(LoggedTestCase):
    def get_url_for_modal_application(self, application):
        return reverse('modal_form', kwargs={'form_name':'application', 'id':application.id})

    def get_url_for_modal_environment(self, application):
        return reverse('modal_form', kwargs={'form_name':'environment', 'parent_name':'application', 'parent_id':application.id})

    def get_url_for_modal_task(self, application):
        return reverse('task_add_form_page', kwargs={'application_id':application.id})


class ApplicationUserTest(ApplicationTest):
    def test_application(self):
        application = ApplicationFactory(department=self.department)
        response = self.client.get('/application/%d/' % application.id)
        self.assertContains(response, application.name)
        self.assertNotContains(response, '"%s"' % self.get_url_for_modal_application(application))
        self.assertNotContains(response, '"%s"' % self.get_url_for_modal_environment(application))
        self.assertNotContains(response, '"%s"' % self.get_url_for_modal_task(application))

    def test_application_forbidden(self):
        application = ApplicationFactory(department=DepartmentFactory())
        response = self.client.get('/application/%d/' % application.id)
        self.assertForbidden(response)


class ApplicationManagerTest(ApplicationTest):
    logged_is_manager = True

    def test_application(self):
        application = ApplicationFactory(department=self.department)
        response = self.client.get('/application/%d/' % application.id)
        self.assertContains(response, application.name)
        self.assertContains(response, '"%s"' % self.get_url_for_modal_application(application))
        self.assertContains(response, '"%s"' % self.get_url_for_modal_environment(application))
        self.assertContains(response, '"%s"' % self.get_url_for_modal_task(application))


class EnvironmentTest(LoggedTestCase):
    def get_url_for_modal_environment(self, environment):
        return reverse('modal_form', kwargs={'form_name':'environment', 'id':environment.id})

    def get_url_for_modal_server(self, environment):
        return reverse('modal_form', kwargs={'form_name':'server', 'parent_name':'environment', 'parent_id':environment.id})


class EnvironmentUserTest(EnvironmentTest):
    def test_environment(self):
        application = ApplicationFactory(department=self.department)
        environment = EnvironmentFactory(application=application)
        response = self.client.get('/environment/%d/' % environment.id)
        self.assertContains(response, environment.name)
        self.assertNotContains(response, '"%s"' % self.get_url_for_modal_environment(environment))
        self.assertNotContains(response, '"%s"' % self.get_url_for_modal_server(environment))

    def test_environment_forbidden(self):
        environment = EnvironmentFactory()
        response = self.client.get('/environment/%d/' % environment.id)
        self.assertForbidden(response)


class EnvironmentManagerTest(EnvironmentTest):
    logged_is_manager = True

    def test_environment(self):
        application = ApplicationFactory(department=self.department)
        environment = EnvironmentFactory(application=application)
        response = self.client.get('/environment/%d/' % environment.id)
        self.assertContains(response, '"%s"' % self.get_url_for_modal_environment(environment))
        self.assertContains(response, '"%s"' % self.get_url_for_modal_server(environment))


class HelpTest(LoggedTestCase):
    def test_help(self):
        response = self.client.get('/help/')
        self.assertContains(response, 'Help')


class SidebarTest(LoggedTestCase):
    def test_options(self):
        department = DepartmentFactory()
        department_invalid = DepartmentFactory()
        self.user.groups.add(department.groups.filter(system_name='user')[0])
        self.user.save()
        response = self.client.get('/help/')
        self.assertContains(response, department.name)
        self.assertContains(response, self.department.name)
        self.assertNotContains(response, department_invalid.name)

    def test_switch_to_valid_department(self):
        response = self.client.get('/department/switch/%d/' % self.department.id)
        self.assertRedirects(response, '/', target_status_code=302)
        self.assertEqual(self.client.session['current_department_id'], self.department.id)

    def test_switch_to_invalid_department(self):
        department = DepartmentFactory()
        response = self.client.get('/department/switch/%d/' % department.id)
        self.assertRedirects(response, '/', target_status_code=302)
        self.assertEqual(self.client.session['current_department_id'], self.department.id)

    def test_application_list(self):
        application_valid = ApplicationFactory(department=self.department)
        application_invalid = ApplicationFactory(department=self.department)
        environment_valid = EnvironmentFactory(application=application_valid)
        environment_invalid = EnvironmentFactory(application=application_valid)
        self.remove_perm_from_user_group('core.view_application', application_invalid)
        self.remove_perm_from_user_group('core.view_environment', environment_invalid)
        response = self.client.get('/help/')
        self.assertContains(response, application_valid.name)
        self.assertNotContains(response, application_invalid.name)
        self.assertContains(response, environment_valid.name)
        self.assertNotContains(response, environment_invalid.name)

    def test_settings(self):
        response = self.client.get('/help/')
        self.assertContains(response, 'Account')
        self.assertNotContains(response, 'Department')
        self.assertNotContains(response, 'System')


class SidebarManagerTest(LoggedTestCase):
    logged_is_manager = True

    def test_settings(self):
        response = self.client.get('/help/')
        self.assertContains(response, 'Account')
        self.assertContains(response, 'Department')
        self.assertNotContains(response, 'System')


class SidebarSuperuserTest(LoggedTestCase):
    logged_is_superuser = True

    def test_settings(self):
        response = self.client.get('/help/')
        self.assertContains(response, 'Account')
        self.assertContains(response, 'Department')
        self.assertContains(response, 'System')

