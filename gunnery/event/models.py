from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from guardian.shortcuts import get_users_with_perms
from core.models import Department


class NotificationPreferences(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notifications")
    event_type = models.CharField(max_length=32, blank=False, null=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "event_type", "content_type", "object_id")

    @staticmethod
    def initialize_for_all_users(department_id, event_type, obj):
        content_type = ContentType.objects.get_for_model(type(obj))
        users = get_users_with_perms(Department(id=department_id))
        for user in users:
            NotificationPreferences(user=user,
                                    event_type=event_type,
                                    content_type=content_type,
                                    object_id=obj.id,
                                    is_active=True).save()


class EventLog(models.Model):
    department = models.ForeignKey(Department, related_name="event_log", db_index=True)
    type = models.CharField(max_length=128, blank=False)
    message = models.TextField()
    time = models.DateTimeField(auto_now=True)