from django.db import models
from django.db.models.signals import post_delete
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from backend.securefile import SecureFileStorage

class Application(models.Model):
	name = models.CharField(blank=False, max_length=128)
	description = models.TextField(blank=True)
	def get_absolute_url(self):
	    return reverse('application_page', args=[str(self.id)])
	def executions_inline(self):
		from task.models import Execution 
		return Execution.objects.filter(task__application_id=self.id).order_by('-time_created')[:3]
	
class Environment(models.Model):
	name = models.CharField(blank=False, max_length=128)
	description = models.TextField(blank=True)
	application = models.ForeignKey(Application, related_name="environments")
	is_production = models.BooleanField(default=False)
	def get_absolute_url(self):
	    return reverse('environment_page', args=[str(self.id)])

	def executions_inline(self):
		from task.models import Execution
		return Execution.objects.filter(environment_id=self.id).order_by('-time_created')[:3]

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
	
	