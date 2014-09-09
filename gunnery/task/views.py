from django.conf import settings
from guardian.shortcuts import get_objects_for_user
import json
from time import strptime
from datetime import datetime
from pytz import UTC, timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from guardian.decorators import permission_required

from .forms import task_create_form, TaskCommandFormset, TaskParameterFormset
from .models import (
    Application, Environment, Execution, ExecutionLiveLog, ExecutionParameter,
    ParameterParser, ServerRole, Task)


@permission_required('task.view_task', (Task, 'id', 'task_id'))
def task_page(request, task_id=None):
    data = {}
    data['task'] = get_object_or_404(Task, pk=task_id)
    return render(request, 'page/task.html', data)


@permission_required('task.execute_task', (Task, 'id', 'task_id'))
def task_execute_page(request, task_id, environment_id=None):
    data = {}
    task = get_object_or_404(Task, pk=task_id)
    data['task'] = task
    form_errors = []
    if environment_id:
        environment = get_object_or_404(Environment, pk=int(environment_id))
        data['environment'] = environment
        if task.application.id != environment.application.id:
            raise ValueError('task.application.id did not match with environment.application.id')

    if request.method == 'POST':
        parameter_prefix = 'parameter-'
        parameters = {}
        for name, value in request.POST.items():
            if name.startswith(parameter_prefix):
                name = name[len(parameter_prefix):]
                parameters[name] = value

        if 'environment' in parameters and parameters['environment']:
            environment = get_object_or_404(Environment, pk=int(parameters['environment']))
            if task.application.id != environment.application.id:
                raise ValueError('task.application.id did not match with environment.application.id')

            duplicateExecution = Execution.objects.filter(task=task, environment=environment,
                                                          status__in=[Execution.PENDING, Execution.RUNNING])
            if duplicateExecution.count():
                form_errors.append('Task %s is already running on %s environment.' %
                                   (task.name, environment.name))
            else:
                with transaction.atomic():
                    execution = Execution(task=task, environment=environment, user=request.user)
                    execution.save()

                    for name, value in parameters.items():
                        if name != 'environment':
                            ExecutionParameter(execution=execution, name=name, value=value).save()

                    parameter_parser = ParameterParser(execution)
                    for command in execution.commands.all():
                        command.command = parameter_parser.process(command.command)
                        command.save()
                execution.start()
                return redirect(execution)
        else:
            form_errors.append('Environment is required')
    data['form_errors'] = form_errors
    data['environments'] = get_objects_for_user(request.user, 'core.execute_environment').filter(
        application=task.application)
    return render(request, 'page/task_execute.html', data)


def task_form_page(request, application_id=None, task_id=None):
    data = {}
    if task_id:
        task = get_object_or_404(Task, pk=task_id)
        application = task.application
        data['task'] = task
        args = {}
        if not request.user.has_perm('task.change_task', task):
            messages.error(request, 'Access denied')
            return redirect('index')
    elif application_id:
        application = get_object_or_404(Application, pk=application_id)
        args = {'application_id': application_id}
        if not request.user.has_perm('core.change_application', application):
            messages.error(request, 'Access denied')
            return redirect('index')
    form, form_parameters, form_commands = create_forms(request, task_id, args)

    if request.method == 'POST':
        form_is_valid = form.is_valid()
        form_parameters_is_valid = form_parameters.is_valid()
        form_commands_is_valid = form_commands.is_valid()
        if form_is_valid and form_parameters_is_valid and form_commands_is_valid:
            task = form.save(commit=False)
            task.save()
            data['task'] = task
            task_save_formset(form_parameters, task)
            task_save_formset(form_commands, task)
            if task_id == None:
                return redirect(task.get_absolute_url())
            request.method = 'GET'
            form, form_parameters, form_commands = create_forms(request, task_id, args)
            request.method = 'POST'
            messages.success(request, 'Saved')

    data['application'] = application
    data['is_new'] = task_id == None
    data['request'] = request
    data['form'] = form
    data['form_parameters'] = form_parameters
    data['form_commands'] = form_commands
    data['server_roles'] = ServerRole.objects.all()
    data['global_parameters'] = ParameterParser.global_parameters.items()
    return render(request, 'page/task_form.html', data)


def create_forms(request, task_id, args):
    form = task_create_form('task', request, task_id, args)
    form_parameters = create_formset(request, TaskParameterFormset, task_id)
    form_commands = create_formset(request, TaskCommandFormset, task_id)

    for form_command in form_commands.forms:
        form_command.fields['roles'].queryset = ServerRole.objects.filter(department_id=request.current_department_id)
    return form, form_parameters, form_commands


def task_save_formset(formset, task):
    formset.save(commit=False)
    for instance in formset.new_objects:
        instance.task_id = task.id
    for form in formset.ordered_forms:
        form.instance.order = form.cleaned_data['ORDER']
        form.instance.save()
    formset.save_m2m()


def create_formset(request, formset, parent_id):
    model = formset.model
    model_queryset = {
        'TaskParameter': model.objects.filter(task_id=parent_id).order_by('order'),
        'TaskCommand': model.objects.filter(task_id=parent_id).order_by('order')
    }
    if request.method == "POST":
        return formset(request.POST,
                       queryset=model_queryset[model.__name__],
                       prefix=model.__name__)
    else:
        return formset(queryset=model_queryset[model.__name__],
                       prefix=model.__name__)


@login_required
def log_page(request, model_name, id):
    #todo add custom permission check
    data = {}
    executions = Execution.objects
    if model_name == 'application':
        executions = executions.filter(environment__application_id=id)
        related = get_object_or_404(Application, pk=id)
    elif model_name == 'environment':
        executions = executions.filter(environment_id=id)
        related = get_object_or_404(Environment, pk=id)
    elif model_name == 'task':
        executions = executions.filter(task_id=id)
        related = get_object_or_404(Task, pk=id)
    elif model_name == 'user':
        executions = executions.filter(user_id=id)
        related = get_object_or_404(get_user_model(), pk=id)
    else:
        raise Http404()
    for related_model in ['task', 'user', 'environment', 'parameters']:
        executions = executions.prefetch_related(related_model)
    data['executions'] = executions.order_by('-time_created')
    data['model_name'] = model_name
    data['related'] = related
    return render(request, 'page/log.html', data)


@permission_required('task.view_task', (Task, 'executions__id', 'execution_id'))
def execution_page(request, execution_id):
    data = {}
    execution = get_object_or_404(Execution, pk=execution_id)
    data['execution'] = execution
    return render(request, 'page/execution.html', data)


@permission_required('task.change_task', (Task, 'id', 'task_id'))
def task_delete(request, task_id):
    if request.method != 'POST':
        return Http404
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    data = {
        'status': True,
        'action': 'redirect',
        'target': task.application.get_absolute_url()
    }
    return HttpResponse(json.dumps(data), content_type="application/json")


@permission_required('task.view_task', (Task, 'executions__id', 'execution_id'))
def live_log(request, execution_id, last_id):
    data = ExecutionLiveLog.objects.filter(execution_id=execution_id, id__gt=last_id).order_by('id').values('id',
                                                                                                            'event',
                                                                                                            'data')
    for item in data:
        item['data'] = json.loads(item['data'])
        for key, value in item['data'].items():
            if key.startswith('time_'):
                value = datetime(*strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")[:6])
                value = value.replace(tzinfo=timezone(settings.TIME_ZONE)).astimezone(request.user.timezone)
                value = request.user.timezone.normalize(value)
                item['data'][key] = value.strftime("%Y-%m-%d %H:%M")
    return HttpResponse(json.dumps(list(data), cls=DjangoJSONEncoder), content_type="application/json")


@permission_required('task.execute_task', (Task, 'executions__id', 'execution_id'))
def execution_abort(request, execution_id):
    # if request.method != 'POST':
    #     return Http404
    execution = get_object_or_404(Execution, pk=execution_id)
    data = {}
    if execution.status in [Execution.PENDING, Execution.RUNNING]:
        execution.status = execution.ABORTED
        execution.save_end()

        ExecutionLiveLog.add(execution_id, 'execution_completed', status=Execution.ABORTED,
                             time=execution.time,
                             time_end=execution.time_end)

        import signal
        from celery.result import AsyncResult
        if execution.celery_task_id:
            AsyncResult(execution.celery_task_id).revoke()
            for commands in execution.commands.all():
                for server in commands.servers.all():
                    if server.celery_task_id:
                        AsyncResult(server.celery_task_id).revoke(terminate=True, signal=signal.SIGALRM)
        data['status'] = True
    else:
        data['status'] = False
    return HttpResponse(json.dumps(list(data), cls=DjangoJSONEncoder), content_type="application/json")