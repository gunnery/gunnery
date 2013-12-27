from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

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

class ExecutionParameter(models.Model):
	execution = models.ForeignKey(Execution, related_name="parameters")
	name = models.CharField(blank=False, max_length=128)
	value = models.CharField(max_length=128)

class ExecutionCommand(models.Model):
	execution = models.ForeignKey(Execution, related_name="commands")
	command = models.TextField()
	roles = models.ManyToManyField(ServerRole)

class ExecutionCommandLog(models.Model):
	execution_command = models.ForeignKey(ExecutionCommand, related_name="logs")
	time_start = models.DateTimeField(blank=True, null=True)
	time_end = models.DateTimeField(blank=True, null=True)
	time = models.IntegerField(blank=True, null=True)
	status = models.IntegerField(blank=True, null=True)
	server = models.ForeignKey(Server)
	output = models.TextField(blank=True)