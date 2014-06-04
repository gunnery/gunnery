from core.tests.base import LoggedTestCase
from .fixtures import *


class TaskTest(LoggedTestCase):
    def setUp(self):
        super(TaskTest, self).setUp()
        application = ApplicationFactory(department=self.department)
        self.task = TaskFactory(application=application)

    def test_form_new(self):
        response = self.client.get('/application/%d/task/' % self.task.application.id)
        self.assertContains(response, 'Add task')

    def test_view(self):
        response = self.client.get('/task/%d/' % self.task.id)
        self.assertContains(response, self.task.name)

    def test_form_edit(self):
        response = self.client.get('/task/%d/edit/' % self.task.id)
        self.assertContains(response, 'Save')

    def test_delete(self):
        response = self.client.post('/task/%d/delete/' % self.task.id)
        self.assertContains(response, 'true')

    def test_execute(self):
        response = self.client.get('/task/%d/execute/' % self.task.id)
        self.assertContains(response, self.task.name)

    def test_list(self):
        response = self.client.get('/application/%d/' % self.task.application.id)
        self.assertContains(response, self.task.name)