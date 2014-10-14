import json
from itertools import chain
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.dispatch import Signal
from django.template import TemplateDoesNotExist
from guardian.shortcuts import get_users_with_perms
from core.models import Department, Application, Server
from event.models import Activity
from django.template.loader import render_to_string
from task.models import Execution, Task


class ModelCreateEvent(object):
    pass


class ModelChangeEvent(object):
    pass


class ExecutionStartEvent(object):
    pass


class ExecutionFinishEvent(object):
    pass


class EventHandler(object):
    @classmethod
    def process(cls, sender=None, department_id=None, user=None, instance=None, signal=None, **kwargs):
        handler = cls()
        handler.sender = sender
        handler.department_id = department_id
        handler.user = user
        handler.instance = instance
        handler.event_type = sender.__name__.replace('Event', '')
        handler.additional_data = kwargs
        return handler._process()

    def __init__(self):
        self.sender = None
        self.department_id = None
        self.user = None
        self.instance = None
        self.event_type = None
        self.additional_data = {}

    def _process(self):
        pass

    def _render(self, filename):
        try:
            print 'event/%s/%s' % (self.event_type, filename)
            return render_to_string('event/%s/%s' % (self.event_type, filename), self.__dict__)
        except TemplateDoesNotExist:
            raise Exception('Template %s not found for event %s' % (filename, self.event_type))


class ActivityHandler(EventHandler):
    """ Saves all events in database EventLog model
    """
    def _process(self):
        users = []
        if isinstance(self.instance, Execution):
            users = get_users_with_perms(self.instance.task, with_superusers=True)
            users_environment = get_users_with_perms(self.instance.environment, with_superusers=True)
            users = users & users_environment
            self.additional_data.update({
                'application_name': self.instance.task.application.name,
                'application_url': self.instance.task.application.get_absolute_url(),
                'environment_name': self.instance.environment.name,
                'task_name': self.instance.task.name,
                'execution_url': self.instance.get_absolute_url()
            })
        elif isinstance(self.instance, Task):
            users = get_users_with_perms(self.instance, with_superusers=True)
            self.additional_data.update({
                'application_name': self.instance.application.name,
                'application_url': self.instance.application.get_absolute_url(),
                'object_name': self.instance.name,
                'object_url': self.instance.get_absolute_url()
            })
        elif isinstance(self.instance, Server):
            users = get_users_with_perms(self.instance.environment, with_superusers=True)
            self.additional_data.update({
                'application_name': self.instance.environment.application.name,
                'application_url': self.instance.environment.application.get_absolute_url(),
                'object_name': self.instance.name,
                'object_url': self.instance.environment.get_absolute_url()
            })

        activity = Activity(author=self.user, type=self.event_type, data=self.to_json())
        activity.save()
        activity.users = users
        activity.save()

    def to_json(self):
        data = {
            'object_model': '%s.%s' % (self.instance._meta.app_label, self.instance._meta.model_name),
            'object_id': self.instance.id
        }
        if self.additional_data:
            data.update(self.additional_data)
        return json.dumps(data)


class UserNotificationHandler(EventHandler):
    """ Sends notification emails
    """
    def _process(self):
        instance = self.instance
        department_id = self.department_id
        signal_type = self.event_type
        users = get_users_with_perms(Department(id=department_id)).prefetch_related('notifications')
        admins = get_user_model().objects.filter(is_superuser=True)
        users = set(chain(users, admins))
        application_content_type = ContentType.objects.get_for_model(Application)
        from backend.tasks import SendEmailTask
        for user in users:
            if not user.has_perm('core.view_environment', instance.environment):
                continue
            if not user.has_perm('task.view_task', instance.task):
                continue
            notification_preference = user.notifications.filter(content_type=application_content_type.id,
                                                                object_id=instance.environment.application_id,
                                                                event_type=signal_type).first()

            if notification_preference and notification_preference.is_active:
                SendEmailTask().delay(subject=self._render('email_subject.txt'),
                                      message=self._render('email_body.txt'),
                                      message_html=self._render('email_body.html'),
                                      recipient=user.email)


gunnery_event = Signal()

_activity_handler = ActivityHandler
gunnery_event.connect(_activity_handler.process, ModelCreateEvent)
gunnery_event.connect(_activity_handler.process, ModelChangeEvent)
gunnery_event.connect(_activity_handler.process, ExecutionStartEvent)
gunnery_event.connect(_activity_handler.process, ExecutionFinishEvent)

_user_notification_handler = UserNotificationHandler
gunnery_event.connect(_user_notification_handler.process, ExecutionFinishEvent)
