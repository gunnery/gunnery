from subprocess import Popen, PIPE, STDOUT
from hashlib import md5
from django.conf import settings
import os


class SecureFileStorage(object):
    """ Handler for storing SSH keys per environment """

    def __init__(self, uid):
        self.files = {
            'private_key': PrivateKey(uid),
            'public_key': PublicKey(uid),
            'known_hosts': KnownHosts(uid),
        }

    def __getattr__(self, name):
        return self.files[name]

    def remove(self):
        for _, secure_file in self.files.items():
            secure_file.remove()


class SecureFile(object):
    """ Base class for secure file """
    prefix = ''

    def __init__(self, uid):
        if isinstance(uid, int):
            uid = str(uid)
        self.uid = uid
        name_hash = md5(settings.SECRET_KEY + self.prefix + uid).hexdigest()
        self.file_name = os.path.join(settings.PRIVATE_DIR, name_hash)

    # if not os.path.exists(self.file_name):
    # 	open(self.file_name, 'w')
    # 	os.chmod(self.file_name, 0700)

    def get_file_name(self):
        return self.file_name

    def read(self):
        return open(self.file_name, 'r').read()

    def remove(self):
        try:
            os.remove(self.file_name)
        except OSError:
            pass


class PrivateKey(SecureFile):
    """ Private key handler """
    prefix = 'private_key'

    def generate(self, comment, remove=True):
        """ Generates private and public key files """
        if remove:
            Popen(['/bin/rm', self.get_file_name()]).communicate()

        command = 'ssh-keygen -f %s -C %s -N \'\'' % (self.get_file_name(), comment)
        process = Popen(command,
                        shell=True,
                        stdout=PIPE,
                        stderr=STDOUT)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise RuntimeError('%s failed with code %d' % (command, process.returncode))

        command = 'mv %s.pub %s' % (self.get_file_name(), PublicKey(self.uid).get_file_name())
        process = Popen(command,
                        shell=True,
                        stdout=PIPE,
                        stderr=STDOUT)
        stdout, stderr = process.communicate()


class PublicKey(SecureFile):
    """ Public key handler """
    prefix = 'public_key'


class KnownHosts(SecureFile):
    """ Known hosts file key handler """
    prefix = 'known_hosts'
