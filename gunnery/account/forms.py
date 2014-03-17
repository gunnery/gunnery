from django.forms import *
from django.contrib.auth import get_user_model

from core.forms import ModalForm, create_form


_user = get_user_model()


class UserForm(ModalForm):
    email = CharField(required=True)
    password = CharField(widget=PasswordInput(render_value=False), required=False, min_length=8)
    name = CharField(label='Name')

    class Meta:
        model = _user
        fields = ['email', 'password', 'name']


class UserSystemForm(ModalForm):
    email = CharField(required=True)
    password = CharField(widget=PasswordInput(render_value=False), required=False, min_length=8)
    name = CharField(label='Name')
    is_superuser = BooleanField(required=False)

    class Meta:
        model = _user
        fields = ['email', 'password', 'name', 'is_superuser']


class UserProfileForm(ModalForm):
    email = CharField(required=True)
    name = CharField(label='Name')

    class Meta:
        model = _user
        fields = ['email', 'name']


class UserPasswordForm(ModalForm):
    password = CharField(widget=PasswordInput(render_value=False), required=False, min_length=8)
    password2 = CharField(widget=PasswordInput(render_value=False), required=False, min_length=8,
                          label="Repeat password")

    class Meta:
        model = _user
        fields = ['password']

    def is_valid(self):
        valid = super(UserPasswordForm, self).is_valid()
        if not valid:
            return valid
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            self._errors['not_match'] = 'Passwords do not match'
            return False
        return True


def account_create_form(name, request, id, args={}):
    form_objects = {
        'user': UserForm if not request.user.is_staff else UserSystemForm,
        'user_profile': UserProfileForm,
        'user_password': UserPasswordForm
    }
    return create_form(form_objects, name, request, id, args)