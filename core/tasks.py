from gunnery.celery import app
from .models import *
from time import sleep
from celery import group, chain, chord

@app.task
def process_execution(execution_id):
	execution = Execution.objects.get(pk=execution_id)
	chord_chain = []
	for command in execution.commands.all():
		tasks = [process_command_on_server.si(log.id) for log in command.logs.all()]
		chord_chain.append( chord( group(tasks), chordfinisher.si() ))
	chain( chord_chain )()
			
@app.task
def chordfinisher( list ):
 	return list

@app.task
def process_command_on_server(execution_command_log_id):
	log = ExecutionCommandLog.objects.get(pk=execution_command_log_id)
	server = log.server
	log.output = 'AAAAA'
	log.save()
	sleep(5)	
