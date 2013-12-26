from django import template
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from core.forms import *
from .main import *
import json

def create_form(name, request, id):
	form_objects = {
		'application': ApplicationForm,
		'environment': EnvironmentForm,
		'server': ServerForm,
		'serverrole': ServerRoleForm,
		'task': TaskForm,
	}
	if not name in form_objects:
		raise Http404
	if id:
		instance = form_objects[name].Meta.model.objects.get(pk=id)
		form = form_objects[name](request.POST or None, instance=instance)
	else:
		form = form_objects[name](request.POST or None)
	return form

def add_relations(instance, parent_name=None, parent_id=None):
	relations = {
		'Environment': ('application', Application),
		'Task': ('application', Application),
		'Server': ('environment', Environment)
	}
	instance_name = type(instance).__name__
	if instance_name in relations:
		relation = relations[instance_name]
		if relation[0] == parent_name:
			setattr(instance, relation[0], relation[1].objects.get(pk=parent_id))

def modal_form(request, form_name, id=None, parent_name=None, parent_id=None):
	form = create_form(form_name, request, id)
	form_template = 'partial/'+form_name+'_form.html'
	is_new = id == None
	if request.method == 'POST':
		template = form_template
		if form.is_valid():
			instance = form.save(commit=False)
			add_relations(instance, parent_name, parent_id)
			instance.save()
			form.save_m2m()
			data = {'status':True, 'action': 'reload'}
			return HttpResponse(json.dumps(data), content_type="application/json")
	else:
		template = 'partial/modal_form.html'
	return render(request, template, {
		'form': form, 
		'form_name': form_name, 
		'form_template': form_template, 
		'is_new': is_new,
		'instance': form.instance,
		'model_name': form.Meta.model.__name__,
		'request': request,
		'server_roles': ServerRole.objects.all()
		})

def modal_delete(request, model_name, id):
	form_objects = {
		'application': Application,
		'environment': Environment,
		'server': Server,
		'serverrole': ServerRole
	}
	if not model_name in form_objects:
		raise Http404
	instance = get_object_or_404(form_objects[model_name], pk=id)
	instance.delete()
	data = {'status':True, 'action': 'reload'}
	return HttpResponse(json.dumps(data), content_type="application/json")