from django import template
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from ..forms import *
from .main import *

def task_page(request, task_id = None):
	data = get_common_page_data()
	data['task'] = get_object_or_404(Task, pk=task_id)
	return render(request, 'page/task.html', data)

def task_execute_page(request, task_id, environment_id=None):
	data = get_common_page_data()
	task = get_object_or_404(Task, pk=task_id)
	data['task'] = task
	if environment_id:
		environment = get_object_or_404(Environment, pk=int(environment_id))
		data['environment'] = environment
		if task.application.id != environment.application.id:
			raise ValueError('task.application.id did not match with environment.application.id')

	if request.method == 'POST':
		parameter_prefix = 'parameter-'
		parameters = {}
		environment_id = request.POST
		for name, value in request.POST.items():
			if name.startswith(parameter_prefix):
				name = name[len(parameter_prefix):]
				parameters[name] = value

		# @todo validate parameter names

		environment = get_object_or_404(Environment, pk=int(parameters['environment']))
		if task.application.id != environment.application.id:
			raise ValueError('task.application.id did not match with environment.application.id')
		execution = Execution(task=task, environment=environment)
		execution.save()

		for name, value in parameters.items():
			if name != 'environment':
				ExecutionParameter(execution=execution, name=name, value=value).save()
		return redirect(execution)

	return render(request, 'page/task_execute.html', data)

def task_form_page(request, application_id = None, task_id = None):
	data = get_common_page_data()
	if task_id:
		task = get_object_or_404(Task, pk=task_id)
		application = task.application
		data['task'] = task
	elif application_id:
		application = get_object_or_404(Application, pk=application_id)

	form = create_form('task', request, task_id)
	form_parameters = create_formset(request, TaskParameterFormset, task_id)
	form_commands = create_formset(request, TaskCommandFormset, task_id)
	
	if request.method == 'POST':
		if form.is_valid() and form_parameters.is_valid() and form_commands.is_valid():
			task = form.save(commit=False)
			task.application = application
			task.save()
			data['task'] = task
			task_save_formset(form_parameters, task)
			task_save_formset(form_commands, task)

	data['application'] = application
	data['is_new'] = task_id == None
	data['request'] = request
	data['form'] = form
	data['form_parameters'] = form_parameters
	data['form_commands'] = form_commands
	data['server_roles'] = ServerRole.objects.all()
	return render(request, 'page/task_form.html', data)

def task_save_formset(formset, task):
	formset.save(commit=False)
	for instance, _ in formset.changed_objects:
		instance.order = 1
		instance.save()
	for instance in formset.new_objects:
		instance.order = 1
		instance.task_id = task.id
		instance.save()
	formset.save_m2m()

def create_formset(request, formset, parent_id):
	model = formset.model
	model_queryset = {
		'TaskParameter': model.objects.filter(task_id=parent_id),
		'TaskCommand': model.objects.filter(task_id=parent_id)
	}
	if request.method == "POST":
		return formset(request.POST, 
			queryset=model_queryset[model.__name__], 
			prefix=model.__name__)
	else:
		return formset(queryset=model_queryset[model.__name__],
			prefix=model.__name__)