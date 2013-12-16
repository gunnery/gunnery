from django.db import models

'''
form django.db import models

class Application(models.Model):
	name = models.CharField(blank=False, max_length=128)
	description = models.TextField()
	
class Environment(models.Model):
	name = models.CharField(blank=False, max_length=128)
	description = models.TextField()
	application = models.ForeignKey(Application)
	is_production = models.BooleanField(default=False)

class Server(models.Model):
	name = models.CharField(blank=False, max_length=128)
	host = models.CharField(blank=False, max_length=128)
	user = models.CharField(blank=False, max_length=128)
	roles = models.ForeignKey(ServerRoles)
	environment = models.ForeignKey(Environment)

class ServerRoles(models.Model):
	name = models.CharField(blank=False, max_length=32)
	
	
class Task(models.Model):
	name = models.CharField(blank=False, max_length=128)
	description = models.TextField()
	application = models.ForeignKey(Application)
	
class TaskParameter(models.Model):
	task = models.ForeignKey(Task)
	name = models.CharField(blank=False, max_length=128)
	default_value = models.CharField(max_length=128)
	description = models.TextField()
	
class TaskCommand(models.Model):
	task = models.ForeignKey(Task)
	command = models.CharField(blank=False, max_length=1024)
	order = models.IntegerField()
	
	
class TaskExecution(models.Model):
	task = models.ForeignKey(Task)
	time_start = models.TimeField()
	time_end = models.TimeField()
	time = models.IntegerField()
	
class TaskExecutionParameter(models.Model):
	task_execution = models.ForeignKey(TaskExecution)
	name = models.CharField(blank=False, max_length=128)
	value = models.CharField(max_length=128)

class TaskExecutionLog(models.Model):
	task_execution = models.ForeignKey(TaskExecution)
	time_start = models.TimeField()
	time_end = models.TimeField()
	time = models.IntegerField()
	command = models.CharField(max_length=1024)
	output = models.TextField()
	status = models.IntegerField()






	
	
from django.db import models
from django.forms import ModelForm

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['name', 'description']

class EnvironmentForm(ModelForm):
    class Meta:
        model = Environment
        fields = ['name', 'description', 'is_production']

class ServerForm(ModelForm):
    class Meta:
        model = Server
        fields = ['name', 'host', 'user', 'roles']

		
class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description']
		
class TaskParameterForm(ModelForm):
    class Meta:
        model = TaskParameter
        fields = ['name', 'default_value', 'description']
		
class TaskCommandForm(ModelForm):
    class Meta:
        model = TaskCommand
        fields = ['command', 'order']

		
class TaskExecutionForm(ModelForm):
    class Meta:
        model = TaskExecution
        fields = []
		
class TaskExecutionParameterForm(ModelForm):
    class Meta:
        model = TaskExecutionParameter
        fields = ['name', 'value']

	'''