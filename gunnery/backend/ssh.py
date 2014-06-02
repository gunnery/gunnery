import select
from paramiko import RSAKey, SSHClient, AutoAddPolicy
from os.path import exists
from .securefile import SecureFileStorage


class Transport(object):
    def __init__(self, server):
        self.server = server
        self.callback = lambda out: None

    def set_stdout_callback(self, callback):
        self.callback = callback


class SSHTransport(Transport):
    output_timeout = 0.5
    output_buffer = 1024

    def __init__(self, server):
        super(SSHTransport, self).__init__(server)
        self.secure_files = SecureFileStorage(self.server.environment_id)
        self.client = self.create_client()
        self.channel = None

    def run(self, command):
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
        private = RSAKey(filename=self.get_private_key_file())
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.load_host_keys(self.get_host_keys_file())
        client.connect(self.server.host, pkey=private, look_for_keys=False, port=self.server.port, username=self.server.user)
        return client

    def close_client(self):
        self.client.save_host_keys(self.get_host_keys_file())
        self.channel.close()
        self.client.close()

    def kill(self):
        self.close_client()

    def get_host_keys_file(self):
        filename = self.secure_files.known_hosts.get_file_name()
        if not exists(filename):
            raise RuntimeError('Known hosts file not found')
        return filename

    def get_private_key_file(self):
        filename = self.secure_files.private_key.get_file_name()
        if not exists(filename):
            raise RuntimeError('Private key file not found')
        return filename


class Server(object):
    def __init__(self):
        self.environment_id = None
        self.host = None
        self.port = None
        self.user = None
        self.authentication_method = 'key'

    @staticmethod
    def from_model(model):
        instance = Server()
        instance.environment_id = model.environment_id
        instance.host = model.host
        instance.port = model.port
        instance.user = model.user
        return instance
