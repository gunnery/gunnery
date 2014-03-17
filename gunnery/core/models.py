from django.db import models
from django.db.models.signals import post_delete
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from backend.securefile import SecureFileStorage


def gunnery_name():
    return RegexValidator(regex='^[a-zA-Z0-9_\.\-]+$', message='Invalid characters')


class Department(models.Model):
    name = models.CharField(blank=False, max_length=128, validators=[gunnery_name()], unique=True)

    class Meta:
        permissions = (
        ("view_department", "Can view department"),
        ("edit_department", "Can edit department"),
        ("execute_department", "Can execute department"),
        ("manage_department", "Can manage department"), )

    def __unicode__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(blank=False, max_length=128, validators=[gunnery_name()])
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, related_name="applications")

    class Meta:
        unique_together = ("department", "name")
        permissions = (
        ("view_application", "Can view application"),
        ("edit_application", "Can edit application"),
        ("execute_application", "Can execute tasks on application"), )

    def get_absolute_url(self):
        return reverse('application_page', args=[str(self.id)])

    def executions_inline(self):
        from task.models import Execution

        return Execution.get_inline_by_application(self.id)


class Environment(models.Model):
    name = models.CharField(blank=False, max_length=128, validators=[gunnery_name()])
    description = models.TextField(blank=True)
    application = models.ForeignKey(Application, related_name="environments")
    is_production = models.BooleanField(default=False)

    class Meta:
        unique_together = ("application", "name")
        permissions = (
        ("view_environment", "Can view environment"),
        ("edit_environment", "Can edit environment"),
        ("execute_environment", "Can execute tasks on environment"), )

    def get_absolute_url(self):
        return reverse('environment_page', args=[str(self.id)])

    def executions_inline(self):
        from task.models import Execution

        return Execution.get_inline_by_environment(self.id)

    def save(self, *args, **kwargs):
        is_new = not self.id
        super(Environment, self).save(*args, **kwargs)
        if is_new:
            from backend.tasks import generate_private_key

            generate_private_key.delay(environment_id=self.id)

    @staticmethod
    def cleanup_files(sender, instance, **kwargs):
        from backend.tasks import cleanup_files

        cleanup_files.delay(instance.id)


post_delete.connect(Environment.cleanup_files, sender=Environment)


class ServerRole(models.Model):
    name = models.CharField(blank=False, max_length=32, validators=[gunnery_name()], unique=True)
    department = models.ForeignKey(Department, related_name="serverroles")

    def __unicode__(self):
        return self.name


class Server(models.Model):
    name = models.CharField(blank=False, max_length=128, validators=[gunnery_name()])
    host = models.CharField(blank=False, max_length=128)
    user = models.CharField(blank=False, max_length=128)
    roles = models.ManyToManyField(ServerRole, related_name="servers")
    environment = models.ForeignKey(Environment, related_name="servers")

    class Meta:
        unique_together = ("environment", "name")
