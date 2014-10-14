from __future__ import unicode_literals
from _socket import gaierror, error as socket_error
from django.core.mail import EmailMultiAlternatives
import logging
import re

from django.conf import settings

from celery import chain, chord
from celery.exceptions import SoftTimeLimitExceeded
from paramiko import AuthenticationException, BadAuthenticationType
from event.dispatcher import gunnery_event, ExecutionFinishEvent

from gunnery.celery import app
from core.models import Environment, Server, ServerAuthentication
from task.models import Execution, ExecutionLiveLog, ExecutionCommandServer
from .securefile import PrivateKey, PublicKey, KnownHosts, SecureFileStorage
import ssh

logger = logging.getLogger(__name__)


@app.task
def _dummy_callback(*args, **kwargs):
    return


@app.task
def generate_private_key(environment_id):
    """ Generate public and private key pair for environment """
    environment = Environment.objects.get(pk=environment_id)
    PrivateKey(environment_id).generate('Gunnery-' + environment.application.name + '-' + environment.name)
    open(KnownHosts(environment_id).get_file_name(), 'w').close()


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
    """ Main celery task responsible for handling task executions

    Creates and queues CommandTask tasks to handle task on specific servers.
    """
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
        """ Returns Execution model

        If model is not found task will retry.
        """
        try:
            return Execution.objects.get(pk=execution_id)
        except Execution.DoesNotExist:
            logger.info('execution %d not found... retry' % execution_id)
            raise self.retry(countdown=5)


class ExecutionTaskFinish(app.Task):
    """ Finishes Execution
    """
    def run(self, execution_id):
        execution = self._get_execution(execution_id)

        if execution.status != Execution.ABORTED:
            failed = running = False
            for command in execution.commands.all():
                for server in command.servers.all():
                    if server.status == server.RUNNING:
                        running = True
                    elif server.status in [None, server.FAILED]:
                        failed = True
            if not running:
                if failed:
                    execution.status = execution.FAILED
                else:
                    execution.status = execution.SUCCESS
                execution.save_end()
                self.finalize(execution, execution_id)
        else:
            self.finalize(execution, execution_id)

    def _get_execution(self, execution_id):
        return Execution.objects.prefetch_related('commands', 'commands__servers').get(pk=execution_id)

    def finalize(self, execution, execution_id):
        """ Trigger event, and save live log
        """
        department_id = execution.environment.application.department.id
        gunnery_event.send(ExecutionFinishEvent,
                           department_id=department_id,
                           instance=execution,
                           status=execution.status)
        ExecutionLiveLog.add(execution_id, 'execution_completed',
                             status=execution.status,
                             time_end=execution.time_end,
                             time=execution.time)


class SoftAbort(Exception):
    pass


class CommandTask(app.Task):
    """ Execute command on specific server
    """
    def __init__(self):
        self.ecs = None
        self.environment_id = None
        self.execution_id = None

    def run(self, execution_command_server_id):
        self._attach_abort_signal()
        self.setup(execution_command_server_id)
        self.execute()
        self.finalize()

    def _attach_abort_signal(self):
        import signal
        signal.signal(signal.SIGALRM, self._sigalrm_handler)

    def _sigalrm_handler(self, signum, frame):
        raise SoftAbort

    def setup(self, execution_command_server_id):
        """ Prepare data
        """
        self.ecs = ExecutionCommandServer.objects.get(pk=execution_command_server_id)
        self.ecs.output = "".encode("utf8")
        if self.ecs.execution_command.execution.status == Execution.ABORTED:
            return
        self.ecs.celery_task_id = self.request.id
        self.ecs.save_start()
        execution = self.ecs.execution_command.execution
        self.environment_id = execution.environment.id
        self.execution_id = execution.id
        ExecutionLiveLog.add(self.execution_id, 'command_started', command_server_id=self.ecs.id)

    def execute(self):
        """ Execute command
        """
        transport = None
        try:
            transport = self.create_transport()
            self.ecs.return_code = transport.run(self.ecs.execution_command.command)
        except BadAuthenticationType:
            self._output_callback('Server does not allow supplied authentication method')
            self.ecs.return_code = 1026
        except AuthenticationException:
            self._output_callback('Key authentication failed')
            self.ecs.return_code = 1026
        except gaierror:
            self._output_callback('Name or service not known')
            self.ecs.return_code = 1027
        except socket_error:
            self._output_callback('Socket error')
            self.ecs.return_code = 1028
        except SoftTimeLimitExceeded:
            line = 'Command failed to finish within time limit (%ds)' % settings.CELERYD_TASK_SOFT_TIME_LIMIT
            self._output_callback(line)
            self.ecs.return_code = 1029
        except SoftAbort:
            if transport:
                logger.info(transport)
                transport.kill()
            self._output_callback('Command execution interrupted by user.')
            self.ecs.return_code = 1025
        except Exception as e:
            import traceback
            logger.error(str(type(e)) + str(e) + "\n" + traceback.format_exc())
            self._output_callback('Unknown error')
            self.ecs.return_code = 1024

    def create_transport(self):
        """ Create SSH connection object
        """
        server = ssh.Server.from_model(self.ecs.server)
        transport = ssh.SSHTransport(server)
        transport.set_stdout_callback(self._output_callback)
        return transport

    def _output_callback(self, output):
        """ Handle output of command

        Remove bash colors and trigger live log event
        """
        output = output.decode("utf8").encode("utf8")
        output = re.sub(r"\x1b\[(\d;)?\d?\dm", "".encode("utf8"), output)
        self.ecs.output += output
        ExecutionLiveLog.add(self.execution_id, 'command_output', command_server_id=self.ecs.id, output=output)

    def finalize(self):
        """ Set command status and trigger live log event
        """
        if self.ecs.return_code == 0:
            self.ecs.status = Execution.SUCCESS
        else:
            self.ecs.status = Execution.FAILED
        self.ecs.save_end()

        ExecutionLiveLog.add(self.execution_id, 'command_completed',
                             command_server_id=self.ecs.id,
                             return_code=self.ecs.return_code,
                             status=self.ecs.status,
                             time=self.ecs.time)


class TestConnectionTask(app.Task):
    """ Task for testing connection with server
    """
    def run(self, server_id):
        status = False
        output = ''
        try:
            transport = self.create_transport(server_id)
            status = transport.run('echo test')
        except AuthenticationException:
            output = 'Key authentication failed'
            status = -1
        except gaierror:
            output = 'Name or service not known'
            status = -1
        except socket_error:
            output = 'Socket error'
            status = -1
        except Exception as e:
            logger.exception('TestConnectionTask server_id=%s: %s %s', server_id, str(type(e)), str(e))
            output = 'Unknown error'
            status = -1
        return status == 0, output

    def create_transport(self, server_id):
        server = ssh.Server.from_model(Server.objects.get(pk=server_id))
        transport = ssh.SSHTransport(server)
        return transport


class SendEmailTask(app.Task):
    """ Send transactional email
    """
    def run(self, subject='', message='', message_html=None, sender=None, recipient=''):
        if not sender:
            sender = settings.EMAIL_NOTIFICATION
        if not subject or not message or not recipient:
            raise Exception('Error sending email, not all required fields were passed')
        message = EmailMultiAlternatives(subject, message, sender, [recipient])
        if message_html:
            message.attach_alternative(message_html, "text/html")
        message.send()
        logging.info('Sent email to %s with subject: %s' % (recipient, subject))


class SaveServerAuthenticationData(app.Task):
    """ In future only backend server will have access to server auth data
    """
    def run(self, server_id, password=''):
        server, created = ServerAuthentication.objects.get_or_create(server_id=server_id)
        if password:
            server.password = password
            server.save()