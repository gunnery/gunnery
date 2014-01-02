import logging
from time import sleep
from celery import group, chain, chord, Task
from django.utils.timezone import now
from gunnery.celery import app
from core.models import *
from .ssh import *
from .securefile import *

logger = logging.getLogger(__name__)

def execution_on_complete(execution):
	execution.time_end = now()
	execution.time = (execution.time_end - execution.time_start).seconds
	for command in execution.commands.all():
		for server in command.servers.all():
			server.output = server.get_live_log_output()
			server.save()


def execution_on_failure(self, exc, task_id, args, kwargs, einfo):
	execution = Execution.objects.get(pk=kwargs['execution_id'])
	execution.status = Execution.FAILED
	execution_on_complete(execution)
	execution.save()

@app.task(ignore_result = True, max_retries = 1, on_failure=execution_on_failure)
def execution_chain(execution_id):
	execution = Execution.objects.get(pk=execution_id)
	execution.time_start = now()
	execution.status = Execution.RUNNING
	execution.save()

	chord_chain = []
	for command in execution.commands.all():
		tasks = [command_process.si(execution_command_server_id=server.id) for server in command.servers.all()]
		chord_chain.append( chord(tasks, _dummy_callback.s()) )
	chord_chain.append(execution_end.si(execution_id))
	chain( chord_chain )()

@app.task(max_retries = 1)
def execution_end(execution_id):
	execution = Execution.objects.get(pk=execution_id)
	execution.status = Execution.SUCCESS
	execution_on_complete(execution)
	execution.save()

def command_on_failure(self, exc, task_id, args, kwargs, einfo):
	command_server = ExecutionCommandServer.objects.get(pk=kwargs['execution_command_server_id'])
	kwargs['execution_id'] = command_server.execution_command.execution_id
	execution_on_failure(self, exc, task_id, args, kwargs, einfo)

@app.task(max_retries = 1, on_failure=command_on_failure)
def command_process(execution_command_server_id):
	command_server = ExecutionCommandServer.objects.get(pk=execution_command_server_id)
	command_server.time_start = now()
	command_server.save()
	server = command_server.server
	environment_id = command_server.execution_command.execution.environment.id

	ssh_private_key = PrivateKey(environment_id)
	ssh_known_hosts = KnownHosts(environment_id)
	ssh_server = Server(server.host, server.user, ssh_private_key, ssh_known_hosts)
	stdout = ssh_server.run(command_server.execution_command.command)

	while True:
		lines = stdout.readline()
		if lines == '':
			break
		ExecutionLiveLog(execution_command_server=command_server, output=lines).save()
	command_server.status = ssh_server.get_status()

	command_server.time_end = now()
	command_server.time = (command_server.time_end - command_server.time_start).seconds
	command_server.save()
	if command_server.status != 0:
		raise Exception('command failed')

@app.task
def _dummy_callback( *args, **kwargs ):
	return
	# logger.warning('dummy_callback')
	# logger.warning('args')
	# for arg in args:
	# 	logger.warning(1,str(type(arg)))
	# 	for arg2 in arg:
	# 		logger.warning(2,str(type(arg2)))
	# logger.warning('kwargs')
	# for name, value in kwargs.items():
	# 	logger.warning(str(type(name)), str(type(value)))

@app.task
def generate_private_key(environment_id):
	environment = Environment.objects.get(pk=environment_id)
	PrivateKey(environment_id).generate('Gunnery-' + environment.application.name + '-' + environment.name)

@app.task
def cleanup_files(environment_id):
	SecureFileStorage(environment_id).remove()
