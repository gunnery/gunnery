from billiard.exceptions import Terminated
import logging
import json
from paramiko import PKey
from time import sleep
from celery import group, chain, chord, Task
from django.conf import settings
from django.utils.timezone import now
from django.core.serializers.json import DjangoJSONEncoder

from gunnery.celery import app
from core.models import *
from task.models import *
from .securefile import *
import ssh

from celery.exceptions import SoftTimeLimitExceeded

logger = logging.getLogger(__name__)


@app.task
def _dummy_callback(*args, **kwargs):
    return


@app.task
def generate_private_key(environment_id):
    """ Generate publi and private key pair for environment """
    environment = Environment.objects.get(pk=environment_id)
    PrivateKey(environment_id).generate('Gunnery-' + environment.application.name + '-' + environment.name)


@app.task
def read_public_key(environment_id):
    """ Return public key contents """
    environment = Environment.objects.get(pk=environment_id)
    return PublicKey(environment_id).read()


@app.task
def cleanup_files(environment_id):
    """ Remove public, private and host keys for envirionment """
    SecureFileStorage(environment_id).remove()


class ExecutionTask(app.Task):
    def __init__(self):
        pass

    def run(self, execution_id):
        execution = self._get_execution(execution_id)
        if execution.status == Execution.ABORTED:
            return
        execution.celery_task_id = self.request.id
        execution.save_start()

        ExecutionLiveLog.add(execution_id, 'execution_started', status=execution.status, time_start=execution.time_start)

        chord_chain = []
        for command in execution.commands.all():
            tasks = [CommandTask().si(execution_command_server_id=server.id) for server in command.servers.all()]
            if len(tasks):
                chord_chain.append(chord(tasks, _dummy_callback.s()))
        chord_chain.append(ExecutionTaskFinish().si(execution_id))
        chain(chord_chain)()

    def _get_execution(self, execution_id):
        return Execution.objects.get(pk=execution_id)


class ExecutionTaskFinish(app.Task):
    def run(self, execution_id):
        execution = self._get_execution(execution_id)
        if execution.status == Execution.ABORTED:
            return
        failed = False
        for command in execution.commands.all():
            for server in command.servers.all():
                if server.status == server.FAILED:
                    failed = True
        if failed:
            execution.status = execution.FAILED
        else:
            execution.status = execution.SUCCESS
        execution.save_end()
        ExecutionLiveLog.add(execution_id, 'execution_completed',
                             status=execution.status,
                             time_end=execution.time_end,
                             time=execution.time)

    def _get_execution(self, execution_id):
        return Execution.objects.get(pk=execution_id)


class SoftAbort(Exception):
    pass


def _sigalrm_handler(signum, frame):
    raise SoftAbort


# from celery.signals import after_task_publish
# @after_task_publish.connect()
# def task_sent_handler(sender=None, body=None, **kwargs):
#     if sender == 'backend.tasks.CommandTask':
#         id = body['kwargs']['execution_command_server_id']
#         execution = Execution.objects.get(pk=id)
#         execution.celery_task_id = body['id']
#         execution.save()


class CommandTask(app.Task):
    def __init__(self):
        pass

    def run(self, execution_command_server_id):
        import signal
        signal.signal(signal.SIGALRM, _sigalrm_handler)
        command_server = ExecutionCommandServer.objects.get(pk=execution_command_server_id)
        if command_server.execution_command.execution.status == Execution.ABORTED:
            return
        command_server.celery_task_id = self.request.id
        command_server.save_start()
        environment_id = command_server.execution_command.execution.environment.id
        execution_id = command_server.execution_command.execution.id

        ExecutionLiveLog.add(execution_id, 'command_started', command_server_id=command_server.id)

        ssh_server = self._get_ssh_server(environment_id, command_server.server)
        self.execute_ssh_command_on_server(command_server, execution_id, ssh_server)

        if command_server.return_code == 0:
            command_server.status = command_server.SUCCESS
        else:
            command_server.status = command_server.FAILED
        command_server.save_end()

        ExecutionLiveLog.add(execution_id, 'command_completed',
                       command_server_id=command_server.id,
                       return_code=command_server.return_code,
                       status=command_server.status,
                       time=command_server.time)

        if command_server.status == command_server.FAILED:
            raise Exception('command exit code != 0')

    def execute_ssh_command_on_server(self, command_server, execution_id, ssh_server):
        stdout = ssh_server.run(command_server.execution_command.command)
        try:
            while True:
                lines = stdout.readline()
                if lines == '':
                    break
                command_server.output += lines
                ExecutionLiveLog.add(execution_id, 'command_output', command_server_id=command_server.id, output=lines)
            command_server.return_code = ssh_server.get_status()
        except SoftTimeLimitExceeded:
            line = 'Command failed to finish within time limit (%ds)' % settings.CELERYD_TASK_SOFT_TIME_LIMIT
            command_server.output += line
            ExecutionLiveLog.add(execution_id, 'command_output', command_server_id=command_server.id, output=line)
            command_server.return_code = 1024
        except SoftAbort:
            ssh_server.kill()
            line = 'Command execution interrupted by user.'
            command_server.output += line
            ExecutionLiveLog.add(execution_id, 'command_output', command_server_id=command_server.id, output=line)
            command_server.return_code = 1025

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
        ssh_server.verbose = True
        status = -1
        output = ''
        try:
            stdout = ssh_server.run('echo test')
            while True:
                line = stdout.readline()
                if line == '':
                    break
                output += line
            status = ssh_server.get_status()
        except Exception:
            pass
        return (status == 0, output)

    def _get_ssh_server(self, server):
        ssh_private_key = PrivateKey(server.environment_id)
        ssh_known_hosts = KnownHosts(server.environment_id)
        return ssh.Server(server.host, server.user, ssh_private_key, ssh_known_hosts)
