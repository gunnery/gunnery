import logging
from time import sleep
from celery import group, chain, chord, Task
from django.utils.timezone import now
from gunnery.celery import app
from core.models import *
from .ssh import SSHCommandRunner

logger = logging.getLogger(__name__)

def execution_on_failure(self, exc, task_id, args, kwargs, einfo):
	execution = Execution.objects.get(pk=kwargs['execution_id'])
	execution.time_end = now()
	execution.status = Execution.FAILED
	execution.time = (execution.time_end - execution.time_start).seconds
	execution.save()

@app.task(ignore_result = True, max_retries = 1, on_failure=execution_on_failure)
def execution_chain(execution_id):
	execution = Execution.objects.get(pk=execution_id)
	execution.time_start = now()
	execution.status = Execution.RUNNING
	execution.save()

	chord_chain = []
	for command in execution.commands.all():
		tasks = [command_process.si(execution_command_log_id=log.id) for log in command.logs.all()]
		chord_chain.append( chord(tasks, _dummy_callback.s()) )
	chord_chain.append(execution_end.si(execution_id))
	chain( chord_chain )()

@app.task(max_retries = 1)
def execution_end(execution_id):
	execution = Execution.objects.get(pk=execution_id)
	execution.time_end = now()
	execution.status = Execution.SUCCESS
	execution.time = (execution.time_end - execution.time_start).seconds
	execution.save()

def command_on_failure(self, exc, task_id, args, kwargs, einfo):
	log = ExecutionCommandLog.objects.get(pk=kwargs['execution_command_log_id'])
	kwargs['execution_id'] = log.execution_command.execution_id
	execution_on_failure(self, exc, task_id, args, kwargs, einfo)

@app.task(max_retries = 1, on_failure=command_on_failure)
def command_process(execution_command_log_id):
	log = ExecutionCommandLog.objects.get(pk=execution_command_log_id)
	log.time_start = now()
	log.save()

	# import random
	# log.output = 'started'
	# log.save()
	# sleep(random.randint(0,6))
	# log.output += ' - finished'
	# log.status = 0
	SSHCommandRunner(log.server, log.execution_command, log).run()

	log.time_end = now()
	log.time = (log.time_end - log.time_start).seconds
	log.save()
	if log.status != 0:
		raise Exception('command failed')

@app.task
def _dummy_callback( *args, **kwargs ):
	logger.warning('dummy_callback')
	logger.warning('args')
	for arg in args:
		logger.warning(1,str(type(arg)))
		for arg2 in arg:
			logger.warning(2,str(type(arg2)))
	logger.warning('kwargs')
	for name, value in kwargs.items():
		logger.warning(str(type(name)), str(type(value)))

