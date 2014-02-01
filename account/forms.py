from django.forms import *
from django.contrib.auth.models import User
from core.forms import ModalForm, create_form

class UserForm(ModalForm):
    email = CharField(required=True)
    password = CharField(widget=PasswordInput(render_value = False), required=False)
    first_name = CharField(label='Name')
    is_superuser = BooleanField(required=False)
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'is_superuser']


def account_create_form(name, request, id, args={}):
	form_objects = {
		'user': UserForm,
	}
	return create_form(form_objects, name, request, id, args)