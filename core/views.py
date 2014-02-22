import json
from django import template
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from .forms import *
from backend.tasks import TestConnectionTask
from django.contrib.auth.decorators import login_required, user_passes_test

def get_common_page_data(request):
	data = {}
	data['application_list_sidebar'] = Application.objects.all().prefetch_related('environments')
	data['user'] = request.user
	return data

@login_required
def index(request):
	data = get_common_page_data(request)
	data['application_list'] = data['application_list_sidebar']
	if not data['application_list']:
		return redirect(reverse('help_page'))
	return render(request, 'page/index.html', data)

@login_required
def application_page(request, application_id):
	data = get_common_page_data(request)
	data['application'] = Application.objects.get(pk=application_id)
	return render(request, 'page/application.html', data)

@login_required
def environment_page(request, environment_id):
	data = get_common_page_data(request)
	data['environment'] = Environment.objects.get(pk=environment_id)
	data['servers'] = Server.objects.filter(environment_id=environment_id).prefetch_related('roles')
	return render(request, 'page/environment.html', data)

@user_passes_test(lambda u: u.is_superuser)
def settings_page(request, section='applications'):
	data = get_common_page_data(request)
	sections = {
		'serverroles': ServerRole.objects.all(),
		'applications': Application.objects.all(),
		'users': User.objects.order_by('email')
	}
	if not section in sections:
		raise Http404()
	data[section] = sections[section]
	data['section'] = section
	return render(request, 'page/settings.html', data)

@login_required
def server_test(request, server_id):
	data = {}
	server = get_object_or_404(Server, pk=server_id)
	data['server'] = get_object_or_404(Server, pk=server_id)
	data['task_id'] = TestConnectionTask().delay(server_id).id
	return render(request, 'partial/server_test.html', data)

@login_required
def server_test_ajax(request, task_id):
	data = {}
	task = TestConnectionTask().AsyncResult(task_id)
	if task.status == 'SUCCESS':
		status, output = task.get()
		data['status'] = status
		data['output'] = output
	elif task.status == 'FAILED':
		data['status'] = False
	else:
		data['status'] = None
	return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def help_page(request):
	data = get_common_page_data(request)
	return render(request, 'page/help.html', data)
