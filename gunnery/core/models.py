import pgcrypto
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from datetime import datetime, timedelta


def gunnery_name():
    return RegexValidator(regex='^[a-zA-Z0-9_\.\-]+$', message='Invalid characters')


class Department(models.Model):
    name = models.CharField(blank=False, max_length=128, validators=[gunnery_name()], unique=True)

    class Meta:
        ordering = ['name']
        permissions = (
        ("view_department", "Can view department"),
        ("execute_department", "Can execute department"), )

    def __unicode__(self):
        return self.name



class Application(models.Model):
    name = models.CharField(blank=False, max_length=128, validators=[gunnery_name()])
    department = models.ForeignKey(Department, related_name="applications")

    class Meta:
        ordering = ['name']
        unique_together = ("department", "name")
        permissions = (
        ("view_application", "Can view application"),
        ("execute_application", "Can execute tasks on application"), )

    def get_absolute_url(self):
        return reverse('application_page', args=[str(self.id)])

    def executions_inline(self):
        from task.models import Execution

        return Execution.get_inline_by_application(self.id)


class Environment(models.Model):
    name = models.CharField(blank=False, max_length=128, validators=[gunnery_name()])
    application = models.ForeignKey(Application, related_name="environments")
    is_production = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        unique_together = ("application", "name")
        permissions = (
        ("view_environment", "Can view environment"),
        ("execute_environment", "Can execute tasks on environment"), )

    def get_absolute_url(self):
        return reverse('environment_page', args=[str(self.id)])

    def executions_inline(self):
        from task.models import Execution

        return Execution.get_inline_by_environment(self.id)

    @staticmethod
    def generate_keys(sender, instance, created, **kwargs):
        """ Generate secure files for environment
        """
        if created:
            from backend.tasks import generate_private_key
            generate_private_key.delay(environment_id=instance.id)

    @staticmethod
    def cleanup_files(sender, instance, **kwargs):
        """ Remove secure files for environment
        """
        from backend.tasks import cleanup_files
        cleanup_files.delay(instance.id)

    def stats_count(self):
        return self.application.tasks.\
            filter(executions__environment=self).\
            annotate(avg=models.Avg('executions__time'), count=models.Count('executions'))

    def stats_statues(self):
        return self.executions.\
            filter(time_start__gte=datetime.now()-timedelta(days=30)).\
            values('status').\
            annotate(count=models.Count('status'))


post_save.connect(Environment.generate_keys, sender=Environment)
post_delete.connect(Environment.cleanup_files, sender=Environment)


class ServerRole(models.Model):
    name = models.CharField(blank=False, max_length=32, validators=[gunnery_name()])
    department = models.ForeignKey(Department, related_name="serverroles")

    class Meta:
        unique_together = ("department", "name")

    def __unicode__(self):
        return self.name

    @staticmethod
    def on_create_department(sender, instance, created, **kwargs):
        for server_role in ['app', 'db', 'cache']:
            ServerRole(name=server_role, department=instance).save()

post_save.connect(ServerRole.on_create_department, sender=Department)


class Server(models.Model):
    OPENSSH_PASSWORD = 1
    OPENSSH_CERTIFICATE = 2
    METHOD_CHOICES = (
        (OPENSSH_CERTIFICATE, 'SSH certificate'),
        (OPENSSH_PASSWORD, 'SSH password'),
    )

    name = models.CharField(blank=False, max_length=128, validators=[gunnery_name()])
    host = models.CharField(blank=False, max_length=128)
    port = models.IntegerField(blank=False, default=22)
    user = models.CharField(blank=False, max_length=128)
    roles = models.ManyToManyField(ServerRole, related_name="servers")
    environment = models.ForeignKey(Environment, related_name="servers")
    method = models.IntegerField(choices=METHOD_CHOICES, default=OPENSSH_CERTIFICATE, verbose_name="Login method")

    class Meta:
        unique_together = ("environment", "name")
        ordering = ['name']


class ServerAuthentication(models.Model):
    server = models.OneToOneField(Server, primary_key=True)
    password = pgcrypto.EncryptedTextField(blank=True)
