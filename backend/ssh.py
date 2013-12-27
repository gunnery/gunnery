from subprocess import Popen, PIPE

# @todo no models here

class SSHCommandRunner(object):
	def __init__(self, server, execution_command, log):
		self.execution_command = execution_command
		self.server = server
		self.log = log
		self.format_command()

	def run(self):
		process = Popen(self.formatted_command.split(' '), 
			bufsize=1,
			stdout=PIPE,
			stderr=PIPE)
		self.log.output = ''
		while True:
			stdout = process.stdout.readline()
			stderr = process.stderr.readline()
			if stdout == '' and stderr == '' and process.poll() != None:
				break
			self.log.output += stdout + stderr
			self.log.save()

		process.communicate()
		self.log.status = process.returncode
		self.log.save()
			

	def format_command(self):
		ssh_options = '-o ConnectTimeout=30 -o ConnectionAttempts=1 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
		parameters = {
			'user': self.server.user,
			'host': self.server.host,
			'command': self.execution_command.command,
			'ssh_options': ssh_options,
		}
		self.formatted_command = 'ssh %(ssh_options)s %(user)s@%(host)s "%(command)s"' % parameters
		print self.formatted_command
