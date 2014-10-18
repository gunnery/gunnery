from django.test import TestCase
from guardian.shortcuts import remove_perm
from account.tests.fixtures import UserFactory
from core.tests.fixtures import ApplicationFactory, DepartmentFactory, EnvironmentFactory
from event.dispatcher import UserNotificationHandler, ExecutionFinishEvent, ActivityHandler, ExecutionStartEvent, \
    ModelChangeEvent
from event.models import Activity
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
        UserNotificationHandler().process(ExecutionFinishEvent, instance=execution)
        self.assertEqual(len(mail.outbox), 1)

    def test_process_with_user_who_cant_view_environment(self):
        remove_perm('core.view_environment', self.user.groups.first(), self.environment)
        remove_perm('core.change_environment', self.user.groups.first(), self.environment)
        remove_perm('core.execute_environment', self.user.groups.first(), self.environment)
        execution = ExecutionFactory(environment=self.environment, task=self.task, user=self.user)
        UserNotificationHandler().process(ExecutionFinishEvent, instance=execution)
        self.assertEqual(len(mail.outbox), 0)

    def test_process_with_user_who_cant_view_task(self):
        remove_perm('task.view_task', self.user.groups.first(), self.task)
        remove_perm('task.change_task', self.user.groups.first(), self.task)
        remove_perm('task.execute_task', self.user.groups.first(), self.task)
        execution = ExecutionFactory(environment=self.environment, task=self.task, user=self.user)
        UserNotificationHandler().process(ExecutionFinishEvent, instance=execution)
        self.assertEqual(len(mail.outbox), 0)


class TestActivityHandler(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.department = DepartmentFactory()
        cls.user = UserFactory()
        cls.user.groups.add(cls.department.groups.get(system_name='user'))
        cls.user.save()
        cls.application = ApplicationFactory(department=cls.department)
        cls.environment = EnvironmentFactory(application=cls.application)
        cls.task = TaskFactory(application=cls.application)

    def test_process_execution(self):
        execution = ExecutionFactory(environment=self.environment, task=self.task, user=self.user)
        ActivityHandler().process(ExecutionStartEvent, user=self.user, instance=execution)
        activity = Activity.objects.order_by('-time').first()
        result = {u'application_url': self.application.get_absolute_url(),
                  u'application_name': self.application.name,
                  u'environment_name': self.environment.name,
                  u'execution_url': execution.get_absolute_url(),
                  u'object_id': execution.id,
                  u'task_name': self.task.name,
                  u'object_model': u'task.execution'}
        self.assertEqual(result, activity.data)

    def test_process_execution_finish(self):
        execution = ExecutionFactory(environment=self.environment, task=self.task, user=self.user)
        ActivityHandler().process(ExecutionFinishEvent, user=self.user,
                                  instance=execution, status=execution.status)
        activity = Activity.objects.order_by('-time').first()
        result = {u'application_url': self.application.get_absolute_url(),
                  u'application_name': self.application.name,
                  u'environment_name': self.environment.name,
                  u'execution_url': execution.get_absolute_url(),
                  u'object_id': execution.id,
                  u'task_name': self.task.name,
                  u'object_model': u'task.execution',
                  u'status': execution.status}
        self.assertEqual(result, activity.data)

    def test_process_task(self):
        ActivityHandler().process(ModelChangeEvent, user=self.user, instance=self.task)
        activity = Activity.objects.order_by('-time').first()
        result = {u'application_url': unicode(self.application.get_absolute_url()),
                  u'application_name': unicode(self.application.name),
                  u'object_id': self.task.id,
                  u'object_url': unicode(self.task.get_absolute_url()),
                  u'object_name': unicode(self.task.name),
                  u'object_model': u'task.task'}
        self.assertEquals(result, activity.data)
