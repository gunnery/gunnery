from django import template
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core.urlresolvers import reverse
from core.forms import *
from .main import *
import json

def modal_form(request, form_name, id=None, parent_name=None, parent_id=None):
	return CoreModal(form_name, id, parent_id).render(request)

def modal_delete(request, form_name, id):
	return CoreModal(form_name, id).delete()

class Modal(object):
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
		return self.get_form_creator()(self.form_name, request, self.id, self.get_form_args())

	def get_form_args(self):
		args = {}
		if self.definition['parent']:
			args[self.definition['parent']] = self.parent_id
		return args

	def render(self, request):
		form = self.create_form(request)
		form_template = 'partial/'+self.form_name+'_form.html'
		is_new = self.id == None
		if request.method == 'POST':
			template = form_template
			if form.is_valid():
				instance = form.save(commit=False)
				instance.save()
				form.save_m2m()
				data = {'status':True, 'action': 'reload'}
				if is_new:
					data = self.trigger_event('create', data, instance)
				return HttpResponse(json.dumps(data), content_type="application/json")
		else:
			template = 'partial/modal_form.html'
		return render(request, template, {
			'form': form, 
			'form_name': self.form_name, 
			'form_template': form_template, 
			'is_new': is_new,
			'instance': form.instance,
			'model_name': form.Meta.model.__name__,
			'request': request,
			'server_roles': ServerRole.objects.all()
			})

	def delete(self):
		instance = get_object_or_404(self.definition['model'], pk=self.id)
		instance.delete()
		data = {'status':True, 'action': 'reload'}
		data = self.trigger_event('delete', data, instance)
		return HttpResponse(json.dumps(data), content_type="application/json")

	def trigger_event(self, name, data, instance):
		name = 'on_'+name
		if name in self.definition:
			callback = getattr(self, self.definition[name])
			data = callback(data, instance)
		return data

class CoreModal(Modal):
	definitions = {
		'application': {
			'form': ApplicationForm,
			'model': Application,
			'parent': None,
			'on_delete': 'on_delete_application',
			'on_create': 'on_create_application' },
		'environment': {
			'form': EnvironmentForm,
			'model': Environment,
			'parent': 'application_id',
			'on_delete': 'on_delete_environment' },
		'server': {
			'form': ServerForm,
			'model': Server,
			'parent': 'environment_id' },
		'serverrole': {
			'form': ServerRoleForm,
			'model': ServerRole,
			'parent': None },
	}

	def get_form_creator(self):
		return core_create_form

	def on_delete_application(self, data, instance):
		data['action'] = 'redirect'
		data['target'] = reverse('settings_page')
		return data

	def on_create_application(self, data, instance):
		data['action'] = 'redirect'
		data['target'] = instance.get_absolute_url()
		return data

	def on_delete_environment(self, data, instance):
		data['action'] = 'redirect'
		data['target'] = instance.application.get_absolute_url()
		return data
