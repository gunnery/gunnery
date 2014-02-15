import json
from django import template
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from .forms import *
from backend.tasks import TestConnectionTask
from django.contrib.auth.decorators import login_required, user_passes_test

def get_common_page_data(request):
	data = {}
	data['application_list_sidebar'] = Application.objects.all()
	data['user'] = request.user
	return data

@login_required
def index(request):
	data = get_common_page_data(request)
	data['application_list'] = Application.objects.all()
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
	return render(request, 'page/environment.html', data)

@user_passes_test(lambda u: u.is_superuser)
def settings_page(request):
	data = get_common_page_data(request)
	data['serverrole'] = ServerRole.objects.all()
	data['applications'] = Application.objects.all()
	data['users'] = User.objects.order_by('email')
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

