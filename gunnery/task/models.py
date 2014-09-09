import json

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import now

from core.models import (
    Application, Environment, gunnery_name, Server, ServerRole)
from event.dispatcher import EventDispatcher
from task.events import ExecutionStart


def _duration(time):
    if time is None:
        return '0s'
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    s = ''
    if hours:
        s += '%dh ' % hours
    if minutes:
        s += '%dm ' % minutes
    if seconds:
        s += '%ds ' % seconds
    return s


class Task(models.Model):
    name = models.CharField(blank=False, max_length=128, validators=[gunnery_name()])
    description = models.TextField(blank=True)
    application = models.ForeignKey(Application, related_name="tasks")

    class Meta:
        unique_together = ("application", "name")
        permissions = (
        ("view_task", "Can view task"),
        ("execute_task", "Can execute task"), )

    def get_absolute_url(self):
        return reverse('task_page', args=[str(self.id)])

    def executions_inline(self):
        return Execution.get_inline_by_task(self.id)

    def commands_ordered(self):
        return self.commands.order_by('order')


class TaskParameter(models.Model):
    task = models.ForeignKey(Task, related_name="parameters")
    name = models.CharField(blank=False, max_length=128, validators=[gunnery_name()])
    default_value = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']


class TaskCommand(models.Model):
    task = models.ForeignKey(Task, related_name="commands")
    command = models.TextField(blank=False)
    roles = models.ManyToManyField(ServerRole, related_name="commands")
    order = models.IntegerField()

    class Meta:
        ordering = ['order']


class StateMixin(object):
    def save_start(self):
        self.time_start = now()
        self.status = self.RUNNING
        self.save()

    def save_end(self, status=None):
        self.time_end = now()
        if self.time_start:
            self.time = (self.time_end - self.time_start).seconds
        if status:
            self.status = status
        self.save()


class Execution(models.Model, StateMixin):
    PENDING = 3
    RUNNING = 0
    SUCCESS = 1
    FAILED = 2
    ABORTED = 4
    STATUS_CHOICES = (
        (PENDING, 'pending'),
        (RUNNING, 'running'),
        (SUCCESS, 'success'),
        (FAILED, 'failed'),
        (ABORTED, 'aborted'),
    )
    task = models.ForeignKey(Task, related_name="executions")
    time_created = models.DateTimeField(auto_now_add=True)
    time_start = models.DateTimeField(blank=True, null=True)
    time_end = models.DateTimeField(blank=True, null=True)
    time = models.IntegerField(blank=True, null=True)
    environment = models.ForeignKey(Environment, related_name="executions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="executions")
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
    celery_task_id = models.CharField(blank=True, max_length=36)

    def get_absolute_url(self):
        return reverse('execution_page', args=[str(self.id)])

    def save(self, *args, **kwargs):
        is_new = not self.id
        super(Execution, self).save(*args, **kwargs)
        if not is_new:
            return
        for command in self.task.commands.all():
            self._create_execution_commands(command)

    def start(self):
        from backend.tasks import ExecutionTask

        ExecutionTask().delay(execution_id=self.id)
        EventDispatcher.trigger(ExecutionStart(self.environment.application.department.id, execution=self))

    def _create_execution_commands(self, command):
        parsed_command = command.command
        execution_command = ExecutionCommand(execution=self, command=parsed_command, order=command.order)
        execution_command.save()
        for role in command.roles.all():
            execution_command.roles.add(role)
        execution_command.save()
        self._create_execution_commands_servers(command, execution_command)

    def _create_execution_commands_servers(self, command, execution_command):
        for server in self.environment.servers.filter(roles__in=command.roles.all()):
            execution_command_server = ExecutionCommandServer(
                execution_command=execution_command,
                server=server)
            execution_command_server.save()

    @staticmethod
    def get_inline_by_query(**kwargs):
        return list(
            Execution.objects.filter(**kwargs).prefetch_related('user').prefetch_related('task').prefetch_related(
                'environment').order_by('-time_created')[:4])

    @staticmethod
    def get_inline_by_application(id):
        return Execution.get_inline_by_query(task__application_id=id)

    @staticmethod
    def get_inline_by_environment(id):
        return Execution.get_inline_by_query(environment_id=id)

    @staticmethod
    def get_inline_by_task(id):
        return Execution.get_inline_by_query(task_id=id)

    @staticmethod
    def get_inline_by_user(id):
        return Execution.get_inline_by_query(user_id=id)

    @property
    def duration(self):
        return _duration(self.time)

    def get_last_log_id(self):
        log = self.live_logs.order_by('id')
        if log.last():
            return log.last().id
        else:
            return None


class ExecutionParameter(models.Model):
    execution = models.ForeignKey(Execution, related_name="parameters")
    name = models.CharField(blank=False, max_length=128)
    value = models.CharField(max_length=128)


class ExecutionCommand(models.Model):
    execution = models.ForeignKey(Execution, related_name="commands")
    command = models.TextField()
    roles = models.ManyToManyField(ServerRole)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']


class ExecutionCommandServer(models.Model, StateMixin):
    PENDING = 3
    RUNNING = 0
    SUCCESS = 1
    FAILED = 2
    STATUS_CHOICES = (
        (PENDING, 'pending'),
        (RUNNING, 'running'),
        (SUCCESS, 'success'),
        (FAILED, 'failed'),
    )
    execution_command = models.ForeignKey(ExecutionCommand, related_name="servers")
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
    time_start = models.DateTimeField(blank=True, null=True)
    time_end = models.DateTimeField(blank=True, null=True)
    time = models.IntegerField(blank=True, null=True)
    return_code = models.IntegerField(blank=True, null=True)
    server = models.ForeignKey(Server)
    # @todo store host, and ip here instead of relation to Server model
    output = models.TextField(blank=True)
    celery_task_id = models.CharField(blank=True, max_length=36)

    class Meta:
        ordering = ['server__name']

    def get_live_log_output(self):
        live_logs = self.live_logs.values_list('output', flat=True)
        return ''.join(live_logs)

    @property
    def duration(self):
        return _duration(self.time)


class ExecutionLiveLog(models.Model):
    execution = models.ForeignKey(Execution, related_name="live_logs")
    event = models.CharField(max_length=128)
    data = models.TextField(blank=True)

    @staticmethod
    def add(execution_id, name, data={}, **kwargs):
        """ Triggers execution event """
        data = dict(data.items() + kwargs.items())
        data = json.dumps(data, cls=DjangoJSONEncoder)
        ExecutionLiveLog(execution_id=execution_id, event=name, data=data).save()


class ParameterParser(object):
    """ Parse command string

    Replace included global variables and task parameters with their values.
    """
    parameter_format = '${%s}'
    global_parameters = {
        'gun_application': 'application name',
        'gun_environment': 'environment name',
        'gun_task': 'task name',
        'gun_user': 'user email',
        'gun_time': 'execution start timestamp'
    }

    def __init__(self, execution):
        self.execution = execution
        import calendar

        self.global_parameter_values = {
            'gun_application': self.execution.task.application.name,
            'gun_environment': self.execution.environment.name,
            'gun_task': self.execution.task.name,
            'gun_user': self.execution.user.email,
            'gun_time': str(calendar.timegm(self.execution.time_created.utctimetuple()))
        }

    def process(self, cmd):
        cmd = self._process_global_parameters(cmd)
        cmd = self._process_parameters(cmd)
        return cmd

    def _process_global_parameters(self, cmd):
        for name, value in self.global_parameter_values.items():
            cmd = cmd.replace(self.parameter_format % name, value)
        return cmd

    def _process_parameters(self, cmd):
        execution_params = self.execution.parameters.all()
        for param in execution_params:
            cmd = cmd.replace(self.parameter_format % param.name, param.value)
        return cmd