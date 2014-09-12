from django.test import TestCase
from guardian.shortcuts import remove_perm
from account.tests.fixtures import UserFactory
from core.tests.fixtures import ApplicationFactory, DepartmentFactory, EnvironmentFactory
from event.dispatcher import UserNotificationHandler
from task.events import ExecutionFinish
from task.tests.fixtures import TaskFactory, ExecutionFactory
from django.core import mail


class TestUserNotificationHandler(TestCase):
    def setUp(self):
        self.department = DepartmentFactory()
        self.user = UserFactory()
        self.user.groups.add(self.department.groups.get(system_name='user'))
        self.user.save()
        self.application = ApplicationFactory(department=self.department)
        self.environment = EnvironmentFactory(application=self.application)
        self.task = TaskFactory(application=self.application)

    def test_process(self):
        execution = ExecutionFactory(environment=self.environment, task=self.task, user=self.user)
        event = ExecutionFinish(self.department.id, execution=execution)
        UserNotificationHandler().process(event)
        self.assertEqual(len(mail.outbox), 1)

    def test_process_with_user_who_cant_view_environment(self):
        remove_perm('core.view_environment', self.user.groups.first(), self.environment)
        execution = ExecutionFactory(environment=self.environment, task=self.task, user=self.user)
        event = ExecutionFinish(self.department.id, execution=execution)
        UserNotificationHandler().process(event)
        self.assertEqual(len(mail.outbox), 0)

    def test_process_with_user_who_cant_view_task(self):
        remove_perm('task.view_task', self.user.groups.first(), self.task)
        execution = ExecutionFactory(environment=self.environment, task=self.task, user=self.user)
        event = ExecutionFinish(self.department.id, execution=execution)
        UserNotificationHandler().process(event)
        self.assertEqual(len(mail.outbox), 0)
