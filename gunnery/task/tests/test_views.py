from core.tests.base import LoggedTestCase
from .fixtures import *


class TaskTest(LoggedTestCase):
    def setUp(self):
        super(TaskTest, self).setUp()
        application = ApplicationFactory(department=self.department)
        self.task = TaskFactory(application=application)

    def test_task_form(self):
        response = self.client.get('/application/%d/task/' % self.task.application.id)
        self.assertContains(response, 'Add task')

    def test_task(self):
        response = self.client.get('/task/%d/' % self.task.id)
        self.assertContains(response, self.task.name)

    def test_execute(self):
        response = self.client.get('/task/%d/execute/' % self.task.id)
        self.assertContains(response, self.task.name)

    def test_list(self):
        response = self.client.get('/application/%d/' % self.task.application.id)
        self.assertContains(response, self.task.name)