from django import template
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import *

def index(request):
	data = get_common_page_data()
	data['application_list'] = Application.objects.all()
	return render(request, 'page/index.html', data)


def application_page(request, application_id):
	data = get_common_page_data()
	data['application'] = Application.objects.get(pk=application_id)
	return render(request, 'page/application.html', data)


def environment_page(request, environment_id):
	data = get_common_page_data()
	data['environment'] = Environment.objects.get(pk=environment_id)
	return render(request, 'page/environment.html', data)


def settings_page(request):
	data = get_common_page_data()
	data['serverrole'] = ServerRole.objects.all()
	data['applications'] = Application.objects.all()
	return render(request, 'page/settings.html', data)

def get_common_page_data():
	data = {}
	data['application_list_sidebar'] = Application.objects.all()
	return data

def create_form(form_objects, name, request, id, args={}):
	if not name in form_objects:
		raise Http404()
	if id:
		instance = form_objects[name].Meta.model.objects.get(pk=id)
		form = form_objects[name](request.POST or None, instance=instance)
	else:
		instance = form_objects[name].Meta.model(**args)
		form = form_objects[name](request.POST or None, instance=instance)
	return form

def core_create_form(name, request, id, args={}):
	form_objects = {
		'application': ApplicationForm,
		'environment': EnvironmentForm,
		'server': ServerForm,
		'serverrole': ServerRoleForm,
	}
	return create_form(form_objects, name, request, id, args)