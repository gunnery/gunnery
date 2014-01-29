import logging
import json
from time import sleep
from celery import group, chain, chord, Task
from django.utils.timezone import now
from django.core.serializers.json import DjangoJSONEncoder
from gunnery.celery import app
from core.models import *
from task.models import *
from .securefile import *
import ssh

logger = logging.getLogger(__name__)

@app.task
def _dummy_callback( *args, **kwargs ):
	return



@app.task
def generate_private_key(environment_id):
	environment = Environment.objects.get(pk=environment_id)
	PrivateKey(environment_id).generate('Gunnery-' + environment.application.name + '-' + environment.name)

@app.task
def read_public_key(environment_id):
	environment = Environment.objects.get(pk=environment_id)
	return PublicKey(environment_id).read()

@app.task
def cleanup_files(environment_id):
	SecureFileStorage(environment_id).remove()


def _trigger_event(execution_id, name, data={}, **kwargs):
	data = dict(data.items() + kwargs.items())
	for key, value in data.items():
		if key.startswith('time_'):
			data[key] = value.strftime('%Y-%m-%d %H:%I')
	data = json.dumps(data, cls=DjangoJSONEncoder)
	ExecutionLiveLog(execution_id=execution_id, event=name, data=data).save()
	
class ExecutionTask(app.Task):
	def __init__(self):
		pass

	def run(self, execution_id):
		execution = self._get_execution(execution_id)
		execution.time_start = now()
		execution.status = Execution.RUNNING
		execution.save()

		_trigger_event(execution_id, 'execution_started', 
			status=execution.status,
			time_start=execution.time_start)

		chord_chain = []
		for command in execution.commands.all():
			tasks = [CommandTask().si(execution_command_server_id=server.id) for server in command.servers.all()]
			if len(tasks):
				chord_chain.append( chord(tasks, _dummy_callback.s()) )
		chord_chain.append(ExecutionTaskFinish().si(execution_id))
		chain( chord_chain )()

	def _get_execution(self, execution_id):
		return Execution.objects.get(pk=execution_id)

class ExecutionTaskFinish(app.Task):
	def run(self, execution_id):
		execution = self._get_execution(execution_id)
		failed = False
		for command in execution.commands.all():
			for server in command.servers.all():
				if server.status == server.FAILED:
					failed = True
		if failed:
			execution.status = execution.FAILED
		else:
			execution.status = execution.SUCCESS
		execution.time_end = now()
		execution.time = (execution.time_end - execution.time_start).seconds
		execution.save()
		_trigger_event(execution_id, 'execution_completed', 
			status=execution.status,
			time_end=execution.time_end,
			time=execution.time)

	def _get_execution(self, execution_id):
		return Execution.objects.get(pk=execution_id)

class CommandTask(app.Task):
	def __init__(self):
		pass

	def run(self, execution_command_server_id):
		command_server = ExecutionCommandServer.objects.get(pk=execution_command_server_id)
		command_server.time_start = now()
		command_server.status = command_server.RUNNING
		command_server.save()
		server = command_server.server
		environment_id = command_server.execution_command.execution.environment.id
		execution_id = command_server.execution_command.execution.id

		_trigger_event(execution_id, 'command_started', 
			command_server_id=command_server.id)

		ssh_server = self._get_ssh_server(environment_id, server)
		stdout = ssh_server.run(command_server.execution_command.command)

		while True:
			lines = stdout.readline()
			if lines == '':
				break
			command_server.output += lines
			_trigger_event(execution_id, 'command_output', command_server_id=command_server.id, output=lines)
		command_server.return_code = ssh_server.get_status()

		if command_server.return_code == 0:
			command_server.status = command_server.SUCCESS
		else:
			command_server.status = command_server.FAILED
		command_server.time_end = now()
		command_server.time = (command_server.time_end - command_server.time_start).seconds
		command_server.save()

		_trigger_event(execution_id, 'command_completed', 
			command_server_id=command_server.id, 
			return_code=command_server.return_code,
			status=command_server.status,
			time=command_server.time)
		if command_server.status == command_server.FAILED:
			raise Exception('command exit code != 0')

	def _get_ssh_server(self, environment_id, server):
		ssh_private_key = PrivateKey(environment_id)
		ssh_known_hosts = KnownHosts(environment_id)
		return ssh.Server(server.host, server.user, ssh_private_key, ssh_known_hosts)

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		command_server = ExecutionCommandServer.objects.get(pk=kwargs['execution_command_server_id'])
		kwargs['execution_id'] = command_server.execution_command.execution_id
		ExecutionTaskFinish().run(execution_id=command_server.execution_command.execution_id)



class TestConnectionTask(app.Task):
	def run(self, server_id):
		server_model = Server.objects.get(pk=server_id)
		ssh_server = self._get_ssh_server(server_model)
		status = -1
		try:
			out = ssh_server.run('echo test')
			while True:
				if out.readline() == '':
					break
			status = ssh_server.get_status()
		except Exception:
			pass
		return status == 0

	def _get_ssh_server(self, server):
		ssh_private_key = PrivateKey(server.environment_id)
		ssh_known_hosts = KnownHosts(server.environment_id)
		return ssh.Server(server.host, server.user, ssh_private_key, ssh_known_hosts)
