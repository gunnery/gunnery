from django.contrib.auth.models import check_password
from django.contrib.auth import get_user_model

_user = get_user_model()

class EmailAuthBackend(object):
    """
    Email Authentication Backend
    
    Allows a user to sign in using an email/password pair rather than
    a username/password pair.
    """
    
    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = _user.objects.get(email=username)
            if user.check_password(password):
                return user
        except _user.DoesNotExist:
            return None 

    def get_user(self, user_id):
        """ Get a _user object from the user_id. """
        try:
            return _user.objects.get(pk=user_id)
        except _user.DoesNotExist:
            return None