from django.test import TestCase
import core.models as models
from core.tests.base import LoggedTestCase


class TaskTest(LoggedTestCase):
	fixtures = ['test_user', 'test_application', 'test_environment', 'test_task']

	def test_task_form(self):
		response = self.client.get('/application/1/task/')
		self.assertContains(response, 'Add task')

	def test_task(self):
		response = self.client.get('/task/1/')
		self.assertContains(response, 'testtask')

	def test_execute(self):
		response = self.client.get('/task/1/execute/')
		self.assertContains(response, 'testtask')

	def test_list(self):
		response = self.client.get('/application/1/')
		self.assertContains(response, 'testtask')