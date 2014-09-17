import json
from itertools import chain
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.template import TemplateDoesNotExist
from guardian.shortcuts import get_users_with_perms
from core.models import Department, Application
from event.models import EventLog
from django.template.loader import render_to_string


class EventHandler(object):
    def __init__(self):
        self.data = {}

    @classmethod
    def process(cls, sender=None, department_id=None, user=None, instance=None, **kwargs):
        print cls, sender
        handler = cls()
        handler.data = {
            'department_id': department_id,
            'user': user,
            'instance': instance,
            'signal_type': sender
        }
        handler.data.update(kwargs)
        return handler._process()

    def _process(self):
        pass

    def _render(self, filename):
        try:
            return render_to_string('event/%s/%s' % (self.data['signal_type'], filename), self.data)
        except TemplateDoesNotExist:
            raise Exception('Template %s not found for event %s' % (filename, self.data['signal_type']))


class LogHandler(EventHandler):
    """ Saves all events in database EventLog model
    """
    def _process(self):
        print 'LogHandler._process'
        EventLog(department_id=self.data['department_id'], type=self.data['signal_type'], message=self.to_json()).save()

    def to_json(self):
        data = {
            'object_model': '%s.%s' % (self.data['instance']._meta.app_label, self.data['instance']._meta.model_name),
            'object_id': self.data['instance'].id,
            'user_id': self.data['user'].id if self.data['user'] else None
        }
        if 'additional_data' in self.data:
            data.update(self.data['additional_data'])
        return json.dumps(data)


class UserNotificationHandler(EventHandler):
    """ Sends notification emails
    """
    def _process(self):
        print 'UserNotificationHandler._process'
        instance = self.data['instance']
        department_id = self.data['department_id']
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
                                                                event_type=type).first()
            if notification_preference and notification_preference.is_active:
                SendEmailTask().delay(subject=self._render('email_subject.txt'),
                                      message=self._render('email_body.txt'),
                                      message_html=self._render('email_body.html'),
                                      recipient=user.email)
import django.dispatch
log_handler = LogHandler
user_notification_handler = UserNotificationHandler
gunnery_event = django.dispatch.Signal()
gunnery_event.connect(log_handler.process, 'ModelChange')
gunnery_event.connect(log_handler.process, 'ExecutionStart')
gunnery_event.connect(log_handler.process, 'ExecutionFinish')
gunnery_event.connect(user_notification_handler.process, 'ExecutionFinish')
