from subprocess import Popen, PIPE, STDOUT


class Server(object):
    """ Creates SSH connection process and streams output """

    def __init__(self, host, user, private_key, known_hosts):
        self.host = host
        self.user = user
        self.private_key = private_key
        self.known_hosts = known_hosts
        self.verbose = False

    def run(self, command):
        """ Run command and return output stream """
        self.command = command
        self.format_command()
        self.process = Popen(self.command_array,
                             bufsize=1,
                             stdout=PIPE,
                             stderr=STDOUT)
        return self.process.stdout

    def get_status(self):
        """ Get return code of command """
        self.process.communicate()
        return self.process.returncode

    def format_command(self):
        """ Prepare ssh command """
        self.command_array = [
            '/usr/bin/ssh',

            '-o ConnectTimeout=30',
            '-o ConnectionAttempts=1',
            '-o StrictHostKeyChecking=no',
            '-o BatchMode=yes',
            '-o UserKnownHostsFile=%s' % self.known_hosts.get_file_name(),  #'-o ControlMaster=auto',
            #'-o ControlPath=/home/celery/.ssh/sockets/%s@%s' % (self.user, self.host),  #'-o ControlPersist=60',

            '-i%s' % self.private_key.get_file_name(),
            '-T',  # Disable pseudo-tty allocation.

            '%s@%s' % (self.user, self.host),
            self.command
        ]
        if self.verbose:
            self.command_array.insert(1, '-v')
        print ' '.join(self.command_array)

