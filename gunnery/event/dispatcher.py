from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.template import TemplateDoesNotExist
from guardian.shortcuts import get_users_with_perms
from core.models import Department, Application
from event.models import EventLog
from django.template.loader import render_to_string


class Event(object):
    context = {}

    def __init__(self, department_id, **kwargs):
        self.department_id = department_id
        for key, value in kwargs.items():
            self.__setattr__(key, value)

    def __setattr__(self, key, value):
        self.context[key] = value

    def __getattr__(self, item):
        return self.context[item] if item in self.context else None

    @property
    def type(self):
        return self.__class__.__name__


class EventDispatcher(object):
    handlers = []

    @classmethod
    def add_handler(cls, handler):
        cls.handlers.append(handler)

    @classmethod
    def trigger(cls, event):
        for handler in cls.handlers:
            handler.process(event)


class EventHandler(object):
    subscribe_to = list()

    def __init__(self):
        self.event = None

    def process(self, event):
        self.event = event
        if len(self.subscribe_to) == 0 or self.event.type in self.subscribe_to:
            self._process(event)

    def _process(self, event):
        pass

    def _render(self, filename):
        try:
            return render_to_string('event/%s/%s' % (self.event.type, filename), self.event.context)
        except TemplateDoesNotExist:
            raise Exception('Template %s not found for event %s' % (filename, self.event.type))

    def get_subject(self):
        return self._render('subject.txt')

    def get_full(self):
        return self._render('full.html')


class LogHandler(EventHandler):
    def _process(self, event):
        EventLog(department_id=event.department_id, type=event.type, message=self.get_subject()).save()
EventDispatcher.add_handler(LogHandler())


class UserNotificationHandler(EventHandler):
    subscribe_to = ('ExecutionFinish',)

    def _process(self, event):
        users = get_users_with_perms(Department(id=event.department_id)).prefetch_related('notifications')
        application_content_type = ContentType.objects.get_for_model(Application)
        messages = []
        for user in users:
            notification_preference = user.notifications.filter(content_type=application_content_type.id,
                                                                object_id=event.execution.environment.application_id,
                                                                event_type=event.type).first()
            if notification_preference and notification_preference.is_active:
                message = mail.EmailMessage(self.get_subject(), self.get_full(), settings.EMAIL_NOTIFICATION,
                                            [user.email])
                messages.append(message)

        if messages:
            connection = mail.get_connection()
            connection.send_messages(messages)
EventDispatcher.add_handler(UserNotificationHandler())