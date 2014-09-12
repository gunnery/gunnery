from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from account.tests.fixtures import UserFactory
from core.tests.fixtures import ApplicationFactory, DepartmentFactory
from event.models import NotificationPreferences


class TestNotificationPreferences(TestCase):
    def setUp(self):
        self.department = DepartmentFactory()
        self.user = UserFactory()
        self.user.groups.add(self.department.groups.get(system_name='user'))
        self.user.save()
        self.application = ApplicationFactory(department=self.department)

    def test_on_save_application(self):
        content_type = ContentType.objects.get_for_model(type(self.application))
        notifications = NotificationPreferences.objects.filter(user=self.user,
                                                               content_type=content_type,
                                                               object_id=self.application.id,
                                                               event_type='ExecutionFinish',
                                                               is_active=True)
        self.assertEqual(len(notifications), 1)

