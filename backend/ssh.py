from subprocess import Popen, PIPE, STDOUT
from cStringIO import StringIO
import os
from hashlib import md5
from time import time
from django.conf import settings

class Server(object):
	def __init__(self, host, user, private_key, known_hosts):
		self.host = host
		self.user = user
		self.private_key = private_key
		self.known_hosts = known_hosts

	def run(self, command):
		self.command = command
		self.format_command()
		self.process = Popen(self.command_array, 
			bufsize=1,
			stdout=PIPE,
			stderr=STDOUT)
		return self.process.stdout

	def get_status(self):
		self.process.communicate()
		return self.process.returncode

	def format_command(self):
		self.command_array =  [
			'/usr/bin/ssh',

			'-o ConnectTimeout=30',
			'-o ConnectionAttempts=1',
			'-o StrictHostKeyChecking=no',
			'-o BatchMode=yes',
			'-o UserKnownHostsFile=%s' % self.known_hosts.get_file_name(),
			#'-o ControlMaster=auto',
			#'-o ControlPath=/home/celery/.ssh/sockets/%s@%s' % (self.user, self.host),
			#'-o ControlPersist=60',

			'-i%s' % self.private_key.get_file_name(),
			'-T', # Disable pseudo-tty allocation.

			'%s@%s' % (self.user, self.host),
			self.command
		]
		print self.command_array

class SecureFile(object):
	prefix = ''
	def __init__(self, uid):
		if isinstance(uid, int):
			uid = str(uid)
		name_hash = md5(self.prefix+uid).hexdigest()
		self.file_name = settings.PRIVATE_DIR + name_hash
		# if not os.path.exists(self.file_name):
		# 	open(self.file_name, 'w')
		# 	os.chmod(self.file_name, 0700)

	def get_file_name(self):
		return self.file_name

	def read(self):
		return open(self.file_name, 'r').read()

class PrivateKey(SecureFile):
	prefix = 'private_key'
	def generate(self, comment, remove=True):
		if remove:
			Popen(['/bin/rm', self.get_file_name() ]).communicate()

		command = '/usr/bin/ssh-keygen -f %s -C %s -N \'\'' % (self.get_file_name(), comment)
		process = Popen(command,
			shell=True,
			stdout=PIPE,
			stderr=STDOUT)
		stdout, stderr = process.communicate()
		if process.returncode != 0:
			raise RuntimeError('%s failed with code %d' % (command, process.returncode))

class KnownHosts(SecureFile):
	prefix = 'known_hosts'
