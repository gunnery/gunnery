from django.forms import *
from django.contrib.auth import get_user_model
from core.forms import ModalForm, create_form

_user = get_user_model()

class UserForm(ModalForm):
    email = CharField(required=True)
    password = CharField(widget=PasswordInput(render_value = False), required=False, min_length=8)
    name = CharField(label='Name')
    is_superuser = BooleanField(required=False)
    class Meta:
        model = _user
        fields = ['email', 'password', 'name', 'is_superuser']

class UserSettingsForm(ModalForm):
    email = CharField(required=True)
    password = CharField(widget=PasswordInput(render_value = False), required=False, min_length=8)
    name = CharField(label='Name')
    class Meta:
        model = _user
        fields = ['email', 'password', 'name']


def account_create_form(name, request, id, args={}):
	form_objects = {
        'user': UserForm,
        'user_settings': UserSettingsForm,
	}
	return create_form(form_objects, name, request, id, args)