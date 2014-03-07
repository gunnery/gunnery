import json
from django import template
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.conf import settings
from core.forms import *
from .views import *

def modal_form(request, form_name, id=None, parent_name=None, parent_id=None, app=None):
	return _get_app_modal(app)(form_name, id, parent_id).render(request)

def modal_delete(request, form_name, id, app='core'):
	return _get_app_modal(app)(form_name, id).delete()

def _get_app_modal(app):
	if app == None:
		obj = Modal
	else:
		if app in settings.INSTALLED_APPS:
			obj = __import__(app, fromlist=['modal']).modal.Modal
		else:
			raise Http404()
	return obj

class BaseModal(object):
	""" Base class for modal dialog boxes """

	""" Defines associated types, their models and forms """
	definitions = {}

	def __init__(self, form_name, id=None, parent_id=None):
		self.form_name = form_name
		self.id = id
		self.parent_id = parent_id
		if form_name in self.definitions:
			self.definition = self.definitions[form_name]
		else:
			raise ValueError('Modal: Unknown form_name')

	def create_form(self, request):
		""" Returns form object """
		return self.get_form_creator()(self.form_name, request, self.id, self.get_form_args())

	def get_form_args(self):
		args = {}
		if self.definition['parent']:
			args[self.definition['parent']] = self.parent_id
		return args

	def render(self, request):
		""" Returns rendered view """
		form = self.create_form(request)
		form = self.trigger_event('form_create', form)
		form_template = 'partial/'+self.form_name+'_form.html'
		is_new = self.id == None
		if request.method == 'POST':
			template = form_template
			if form.is_valid():
				try:
					form = self.trigger_event('before_save', {'form': form})['form']
					instance = form.save()
					data = {'status':True, 'action': 'reload'}
				
					if is_new:
						data = self.trigger_event('create', {'data': data, 'instance': instance})['data']
					else:
						data = self.trigger_event('update', {'data': data, 'instance': instance})['data']
					return HttpResponse(json.dumps(data), content_type="application/json")
				except IntegrityError as e:
					from django.forms.util import ErrorList
					errors = form._errors.setdefault("__all__", ErrorList())
					errors.append('Integrity error')
					errors.append(e)

		else:
			template = 'partial/modal_form.html'
		data = {
			'form': form, 
			'form_template': form_template, 
			'is_new': is_new,
			'instance': form.instance,
			'model_name': form.Meta.model.__name__,
			'request_path': request.path
		}
		data = self.trigger_event('view', data)
		return render(request, template, data)

	def delete(self):
		""" Handles delete on modal model """
		instance = get_object_or_404(self.definition['model'], pk=self.id)
		instance.delete()
		data = {'status':True, 'action': 'reload'}
		data = self.trigger_event('delete', {'data': data, 'instance': instance})['data']
		return HttpResponse(json.dumps(data), content_type="application/json")

	def trigger_event(self, event, data={}):
		""" Triggers modal event """
		event = 'on_%s_%s' % (event, self.form_name)
		try:
			callback = getattr(self, event)
			data = callback(data)
		except AttributeError:
			pass
		return data

class Modal(BaseModal):
	definitions = {
		'application': {
			'form': ApplicationForm,
			'model': Application,
			'parent': None, },
		'environment': {
			'form': EnvironmentForm,
			'model': Environment,
			'parent': 'application_id', },
		'server': {
			'form': ServerForm,
			'model': Server,
			'parent': 'environment_id' },
		'serverrole': {
			'form': ServerRoleForm,
			'model': ServerRole,
			'parent': None }
	}

	def get_form_creator(self):
		return core_create_form

	def on_create_application(self, data):
		data['data']['action'] = 'redirect'
		data['data']['target'] = data['instance'].get_absolute_url()
		return data

	def on_delete_application(self, data):
		data['data']['action'] = 'redirect'
		data['data']['target'] = reverse('settings_page')
		return data

	def on_delete_environment(self, data):
		data['data']['action'] = 'redirect'
		data['data']['target'] = data['instance'].application.get_absolute_url()
		return data

	def on_view_server(self, data):
		from backend.tasks import read_public_key
		try:
			data['pubkey'] = read_public_key.delay(data['instance'].environment_id).get()
		except Exception as e:
			data['pubkey'] = 'Couldn\'t load'
		return data
