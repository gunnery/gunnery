from django.db import models
from django.db.models.signals import post_delete
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from backend.tasks import *
from backend.securefile import SecureFileStorage

class Application(models.Model):
	name = models.CharField(blank=False, max_length=128)
	description = models.TextField(blank=True)
	def get_absolute_url(self):
	    return reverse('application_page', args=[str(self.id)])
	def executions_inline(self):
		return Execution.objects.filter(task__application_id=self.id).order_by('-time_created')[:3]
	
class Environment(models.Model):
	name = models.CharField(blank=False, max_length=128)
	description = models.TextField(blank=True)
	application = models.ForeignKey(Application, related_name="environments")
	is_production = models.BooleanField(default=False)
	def get_absolute_url(self):
	    return reverse('environment_page', args=[str(self.id)])

	def executions_inline(self):
		return Execution.objects.filter(environment_id=self.id).order_by('-time_created')[:3]

	def save(self, *args, **kwargs):
		is_new = not self.id
		super(Environment, self).save(*args, **kwargs)
		if is_new:
			generate_private_key.delay(environment_id=self.id)

	@staticmethod
	def cleanup_files(sender, instance, **kwargs):
		cleanup_files.delay(instance.id)

post_delete.connect(Environment.cleanup_files)


class ServerRole(models.Model):
	name = models.CharField(blank=False, max_length=32)
	def __unicode__(self):
		return self.name

class Server(models.Model):
	name = models.CharField(blank=False, max_length=128)
	host = models.CharField(blank=False, max_length=128)
	user = models.CharField(blank=False, max_length=128)
	roles = models.ManyToManyField(ServerRole, related_name="servers")
	environment = models.ForeignKey(Environment, related_name="servers")
	
	
class Task(models.Model):
	name = models.CharField(blank=False, max_length=128)
	description = models.TextField(blank=True)
	application = models.ForeignKey(Application, related_name="tasks")
	def get_absolute_url(self):
	    return reverse('task_page', args=[str(self.id)])
	def executions_inline(self):
		return Execution.objects.filter(task_id=self.id).order_by('-time_created')[:3]
	
class TaskParameter(models.Model):
	task = models.ForeignKey(Task, related_name="parameters")
	name = models.CharField(blank=False, max_length=128, 
		validators=[RegexValidator(regex='^[a-zA-Z0-9_\.\-]+$', message='Invalid characters')])
	default_value = models.CharField(max_length=128)
	description = models.TextField(blank=True)
	order = models.IntegerField()
	
class TaskCommand(models.Model):
	task = models.ForeignKey(Task, related_name="commands")
	command = models.TextField(blank=False)
	roles = models.ManyToManyField(ServerRole, related_name="commands")
	order = models.IntegerField()
	

	
class Execution(models.Model):
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
	task = models.ForeignKey(Task, related_name="executions")
	time_created = models.DateTimeField(auto_now_add=True)
	time_start = models.DateTimeField(blank=True, null=True)
	time_end = models.DateTimeField(blank=True, null=True)
	time = models.IntegerField(blank=True, null=True)
	environment = models.ForeignKey(Environment, related_name="executions")
	status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
	def get_absolute_url(self):
		return reverse('execution_page', args=[str(self.id)])

	def save(self, *args, **kwargs):
		is_new = not self.id
		super(Execution, self).save(*args, **kwargs)
		if not is_new:
			return
		for command in self.task.commands.all():
			self._create_execution_commands(command)
		execution_chain.delay(execution_id=self.id)

	def _create_execution_commands(self, command):
		parsed_command = command.command
		execution_command = ExecutionCommand(execution=self, command=parsed_command)
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

class ExecutionParameter(models.Model):
	execution = models.ForeignKey(Execution, related_name="parameters")
	name = models.CharField(blank=False, max_length=128)
	value = models.CharField(max_length=128)

class ExecutionCommand(models.Model):
	execution = models.ForeignKey(Execution, related_name="commands")
	command = models.TextField()
	roles = models.ManyToManyField(ServerRole)

class ExecutionCommandServer(models.Model):
	execution_command = models.ForeignKey(ExecutionCommand, related_name="servers")
	time_start = models.DateTimeField(blank=True, null=True)
	time_end = models.DateTimeField(blank=True, null=True)
	time = models.IntegerField(blank=True, null=True)
	status = models.IntegerField(blank=True, null=True)
	server = models.ForeignKey(Server)
	# @todo store host, and ip here instead of relation to Server model
	output = models.TextField(blank=True)
	def get_live_log_output(self):
		live_logs = self.live_logs.values_list('output', flat=True)
		return ''.join(live_logs)

class ExecutionLiveLog(models.Model):
	execution_command_server = models.ForeignKey(ExecutionCommandServer, related_name="live_logs")
	output = models.TextField(blank=True)