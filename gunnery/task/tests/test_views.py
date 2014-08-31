from guardian.shortcuts import remove_perm
from core.tests.base import LoggedTestCase
from core.tests.fixtures import ServerRoleFactory, DepartmentFactory, EnvironmentFactory
from .fixtures import *


class TaskTest(LoggedTestCase):
    def setUp(self):
        super(TaskTest, self).setUp()
        self.application = ApplicationFactory(department=self.department)
        self.task = TaskFactory(application=self.application)

    def test_form_create_forbidden(self):
        application = ApplicationFactory(department=self.department)
        response = self.client.get('/application/%d/task/' % application.id)
        self.assertForbidden(response)

    def test_view(self):
        response = self.client.get('/task/%d/' % self.task.id)
        self.assertContains(response, self.task.name)
        self.assertContains(response, reverse('task_execute_page', kwargs={'task_id': self.task.id}))
        self.assertNotContains(response, reverse('task_form_page', kwargs={'task_id': self.task.id}))

    def test_view_execute_forbidden(self):
        self.remove_perm_from_user_group('task.execute_task', self.task)
        response = self.client.get('/task/%d/' % self.task.id)
        self.assertContains(response, self.task.name)
        self.assertNotContains(response, reverse('task_execute_page', kwargs={'task_id': self.task.id}))

    def test_view_forbidden_department(self):
        application = ApplicationFactory(department=DepartmentFactory())
        task = TaskFactory(application=application)
        response = self.client.get('/task/%d/' % task.id)
        self.assertForbidden(response)

    def test_view_forbidden_task(self):
        self.remove_perm_from_user_group('task.view_task', self.task)
        response = self.client.get('/task/%d/' % self.task.id)
        self.assertForbidden(response)

    def test_execute(self):
        environment_valid = EnvironmentFactory(application=self.application)
        environment_invalid = EnvironmentFactory(application=self.application)
        self.remove_perm_from_user_group('core.execute_environment', environment_invalid)
        response = self.client.get('/task/%d/execute/' % self.task.id)
        self.assertContains(response, self.task.name)
        self.assertContains(response, environment_valid.name+"</option>")
        self.assertNotContains(response, environment_invalid.name+"</option>")
        self.assertNotContains(response, reverse('task_form_page', kwargs={'task_id': self.task.id}))

    def test_execute_forbidden(self):
        self.remove_perm_from_user_group('task.execute_task', self.task)
        response = self.client.get('/task/%d/execute/' % self.task.id)
        self.assertForbidden(response)

    def test_execute_forbidden_change(self):
        self.remove_perm_from_user_group('task.change_task', self.task)
        response = self.client.get('/task/%d/execute/' % self.task.id)
        self.assertNotContains(response, reverse('task_form_page', kwargs={'task_id': self.task.id}))

    def test_list(self):
        response = self.client.get('/application/%d/' % self.task.application.id)
        self.assertContains(response, self.task.name)

    def test_execution(self):
        environment = EnvironmentFactory(application=self.application)
        execution = ExecutionFactory(task=self.task, environment=environment, user=self.user)
        response = self.client.get('/execution/%d/' % execution.id)
        self.assertContains(response, self.task.name)
        self.assertContains(response, environment.name)
        self.assertContains(response, reverse('task_execute_page', kwargs={'task_id': self.task.id}))
        self.assertNotContains(response, reverse('task_form_page', kwargs={'task_id': self.task.id}))

    def test_execution_forbidden_change(self):
        self.remove_perm_from_user_group('task.change_task', self.task)
        self.remove_perm_from_user_group('task.execute_task', self.task)
        environment = EnvironmentFactory(application=self.application)
        execution = ExecutionFactory(task=self.task, environment=environment, user=self.user)
        response = self.client.get('/execution/%d/' % execution.id)
        self.assertContains(response, self.task.name)
        self.assertContains(response, environment.name)
        self.assertNotContains(response, reverse('task_execute_page', kwargs={'task_id': self.task.id}))
        self.assertNotContains(response, reverse('task_form_page', kwargs={'task_id': self.task.id}))

    def test_execution_forbidden(self):
        environment = EnvironmentFactory(application=self.application)
        execution = ExecutionFactory(task=self.task, environment=environment, user=self.user)
        self.remove_perm_from_user_group('core.view_task', self.task)
        response = self.client.get('/execution/%d/' % execution.id)
        self.assertForbidden(response)

    def test_form_edit_forbidden(self):
        response = self.client.get('/task/%d/edit/' % self.task.id)
        self.assertForbidden(response)

class TaskManagerTest(LoggedTestCase):
    logged_is_manager = True

    def setUp(self):
        super(TaskManagerTest, self).setUp()
        self.application = ApplicationFactory(department=self.department)
        self.task = TaskFactory(application=self.application)

    def test_view(self):
        response = self.client.get('/task/%d/' % self.task.id)
        self.assertContains(response, reverse('task_form_page', kwargs={'task_id': self.task.id}))

    def test_execute(self):
        response = self.client.get('/task/%d/execute/' % self.task.id)
        self.assertContains(response, reverse('task_form_page', kwargs={'task_id': self.task.id}))

    def test_execution(self):
        environment = EnvironmentFactory(application=self.application)
        execution = ExecutionFactory(task=self.task, environment=environment, user=self.user)
        response = self.client.get('/execution/%d/' % execution.id)
        self.assertContains(response, reverse('task_form_page', kwargs={'task_id': self.task.id}))

    def test_delete(self):
        response = self.client.post('/task/%d/delete/' % self.task.id)
        self.assertContains(response, 'true')

    def test_form_edit(self):
        response = self.client.get('/task/%d/edit/' % self.task.id)
        self.assertContains(response, 'Save')

    def test_form_create(self):
        response = self.client.get('/application/%d/task/' % self.task.application.id)
        self.assertContains(response, 'Add task')

    def test_create(self):
        server_role = ServerRoleFactory(department=self.department)
        data = {'name': 'TaskName',
                'TaskCommand-0-ORDER': '1',
                'TaskCommand-0-command': 'echo 123',
                'TaskCommand-0-roles': server_role.id,
                'application': self.application.id,
                'TaskParameter-TOTAL_FORMS': 1,
                'TaskParameter-INITIAL_FORMS': 0,
                'TaskParameter-MAX_NUM_FORMS': 1000,
                'TaskCommand-TOTAL_FORMS': 2,
                'TaskCommand-INITIAL_FORMS': 0,
                'TaskCommand-MAX_NUM_FORMS': 1000}
        self.client.post('/application/%d/task/' % self.task.application.id, data)
        try:
            Task.objects.get(name='TaskName')
        except Task.DoesNotExist:
            self.fail('Task not created')