import select
from paramiko import RSAKey, SSHClient, AutoAddPolicy
from os.path import exists
from .securefile import SecureFileStorage


class Transport(object):
    """ Base transport protocol class
    """
    def __init__(self, server):
        self.server = server
        self.callback = lambda out: None

    def set_stdout_callback(self, callback):
        self.callback = callback


class SSHTransport(Transport):
    """ SSH connection
    """
    output_timeout = 0.5
    output_buffer = 1024

    def __init__(self, server):
        super(SSHTransport, self).__init__(server)
        self.secure_files = SecureFileStorage(self.server.environment_id)
        self.client = self.create_client()
        self.channel = None

    def run(self, command):
        """ Execute command in current connection

        Handle output using attached callback function
        """
        self.channel = self.client.get_transport().open_session()
        self.channel.get_pty()
        self.channel.exec_command(command)
        while True:
            rl, _, _ = select.select([self.channel], [], [], self.output_timeout)
            if len(rl) > 0:
                output = self.channel.recv(self.output_buffer)
                if output:
                    self.callback(output)
                else:
                    break
        return self.channel.recv_exit_status()

    def create_client(self):
        """ Create and configure SSHClient
        """
        private = RSAKey(filename=self.get_private_key_file())
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.load_host_keys(self.get_host_keys_file())
        if self.server.authentication_method == self.server.OPENSSH_PASSWORD:
            client.connect(self.server.host, password=self.server.password,
                           look_for_keys=False, port=self.server.port, username=self.server.user)
        elif self.server.authentication_method == self.server.OPENSSH_CERTIFICATE:
            client.connect(self.server.host, pkey=private,
                           look_for_keys=False, port=self.server.port, username=self.server.user)
        return client

    def close_client(self):
        """ Close SSHClient
        """
        self.client.save_host_keys(self.get_host_keys_file())
        if self.channel:
            self.channel.close()
        self.client.close()

    def kill(self):
        """ Alias for close_client method
        """
        self.close_client()

    def get_host_keys_file(self):
        """ Return path to known hosts file
        """
        filename = self.secure_files.known_hosts.get_file_name()
        if not exists(filename):
            raise RuntimeError('Known hosts file not found')
        return filename

    def get_private_key_file(self):
        """ Return path to private key file
        """
        filename = self.secure_files.private_key.get_file_name()
        if not exists(filename):
            raise RuntimeError('Private key file not found')
        return filename


class Server(object):
    """ Server model
    """
    OPENSSH_PASSWORD = 1
    OPENSSH_CERTIFICATE = 2

    def __init__(self):
        self.environment_id = None
        self.host = None
        self.port = None
        self.user = None
        self.authentication_method = 'key'
        self.password = None

    @staticmethod
    def from_model(model):
        instance = Server()
        instance.environment_id = model.environment_id
        instance.host = model.host
        instance.port = model.port
        instance.user = model.user
        instance.password = model.serverauthentication.password
        instance.authentication_method = model.method
        return instance
