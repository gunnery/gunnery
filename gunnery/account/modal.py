from core.modal import BaseModal
from django.contrib.auth import get_user_model
from .forms import account_create_form

_user = get_user_model()

class Modal(BaseModal):
	definitions = {
		'user': {
			'model': _user,
			'parent': None
		}
	}

	def get_form_creator(self):
		return account_create_form

	def on_update_user(self, data):
		data['instance'].save()
		return data

	def on_before_save_user(self, data):
		instance = data['form'].instance
		instance.username = instance.email
		if len(instance.password):
			instance.set_password(instance.password)
		else:
			instance.password = _user.objects.get(pk=instance.id).password
		return data

	def on_form_create_user(self, form):
		if form.instance.id == None:
			form.fields['password'].required = True
		return form