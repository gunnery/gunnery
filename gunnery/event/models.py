from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
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


class EventLog(models.Model):
    department = models.ForeignKey(Department, related_name="event_log", db_index=True)
    type = models.CharField(max_length=128, blank=False)
    message = models.TextField()
    time = models.DateTimeField(auto_now=True)