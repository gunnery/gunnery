from django.contrib.contenttypes.models import ContentType
import json

from django.http import Http404, HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render
from guardian.decorators import permission_required

from guardian.shortcuts import get_objects_for_user

from account.models import DepartmentGroup
from backend.tasks import TestConnectionTask
from event.models import NotificationPreferences
from .models import Application, Department, Environment, Server, ServerRole
from task.models import Execution


@login_required
def index(request):
    data = {}
    executions = Execution.objects.filter(task__application__department_id=request.current_department_id)
    if not executions.count():
        return redirect(reverse('first_steps_page'))
    return render(request, 'page/index.html', data)


@permission_required('core.view_application', (Application, 'id', 'application_id'))
def application_page(request, application_id):
    data = {}
    data['application'] = get_object_or_404(Application, pk=application_id)
    return render(request, 'page/application.html', data)


@permission_required('core.view_environment', (Environment, 'id', 'environment_id'))
def environment_page(request, environment_id):
    data = {}
    data['environment'] = get_object_or_404(Environment, pk=environment_id)
    data['servers'] = list(Server.objects.filter(environment_id=environment_id).prefetch_related('roles'))
    return render(request, 'page/environment.html', data)


@permission_required('core.view_environment', (Environment, 'servers__id', 'server_id'))
def server_test(request, server_id):
    data = {}
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
def first_steps_page(request):
    data = {}
    return render(request, 'page/first_steps.html', data)


@login_required
def settings_page(request, section='user', subsection='profile'):
    data = {}
    data['section'] = section
    data['subsection'] = subsection
    data['department'] = Department(pk=request.current_department_id)
    data['on_settings'] = True
    handler = '_settings_%s_%s' % (section, subsection)
    if section == 'system' and request.user.is_superuser is not True:
        return redirect('index')
    if section == 'department' and not request.user.has_perm('core.change_department', obj=data['department']):
        return redirect('index')
    if handler in globals():
        data = globals()[handler](request, data)
    else:
        raise Http404
    return render(request, 'page/settings.html', data)


def _settings_account_profile(request, data):
    data['subsection_template'] = 'partial/account_profile.html'
    from account.forms import account_create_form
    form = account_create_form('user_profile', request, request.user.id)
    form.fields['email'].widget.attrs['readonly'] = True
    data['form'] = form
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['user'] = form.instance
            messages.success(request, 'Saved')
    return data


def _settings_account_password(request, data):
    data['subsection_template'] = 'partial/account_password.html'
    from account.forms import account_create_form
    form = account_create_form('user_password', request, request.user.id)
    data['form'] = form
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            data['user'] = form.instance
            messages.success(request, 'Saved')
    return data


def _settings_account_notifications(request, data):
    data['subsection_template'] = 'partial/account_notifications.html'
    data['applications'] = get_objects_for_user(request.user, 'core.view_application')
    content_type = ContentType.objects.get_for_model(Application)
    if request.method == 'POST':
        for application in data['applications']:
            key = 'notification[%s]' % application.id
            notification, created = NotificationPreferences.objects.get_or_create(
                user=request.user,
                event_type='ExecutionFinish',
                content_type=content_type,
                object_id=application.id)
            if notification.is_active != (key in request.POST):
                notification.is_active = key in request.POST
                notification.save()
        messages.success(request, 'Saved')
    data['notifications'] = NotificationPreferences.objects.filter(
        user=request.user,
        event_type='ExecutionFinish',
        content_type=content_type.id).values_list('object_id', 'is_active')
    data['notifications'] = dict(data['notifications'])
    return data


def _settings_department_applications(request, data):
    data['subsection_template'] = 'partial/application_list.html'
    data['applications'] = Application.objects.filter(department_id=request.current_department_id)
    data['empty'] = not bool(data['applications'].count())
    return data


def _settings_department_users(request, data):
    data['subsection_template'] = 'partial/user_list.html'
    from guardian.shortcuts import get_users_with_perms
    department = Department.objects.get(pk=request.current_department_id)
    data['users'] = get_users_with_perms(department).prefetch_related('groups__departmentgroup').order_by('name')
    data['department_user_list'] = True
    data['form_name'] = 'user'
    return data


def _settings_department_groups(request, data):
    data['subsection_template'] = 'partial/group_list.html'
    data['groups'] = DepartmentGroup.objects.filter(department_id=request.current_department_id)
    return data


def _settings_department_serverroles(request, data):
    data['subsection_template'] = 'partial/serverrole_list.html'
    data['serverroles'] = ServerRole.objects.filter(department_id=request.current_department_id)
    data['empty'] = not bool(data['serverroles'].count())
    return data


@user_passes_test(lambda u: u.is_superuser)
def _settings_system_departments(request, data):
    data['subsection_template'] = 'partial/department_list.html'
    data['departments'] = Department.objects.all()
    return data


@user_passes_test(lambda u: u.is_superuser)
def _settings_system_users(request, data):
    data['subsection_template'] = 'partial/user_list.html'
    data['users'] = get_user_model().objects.exclude(id=-1).prefetch_related('groups__departmentgroup__department').order_by('name')
    data['form_name'] = 'usersystem'
    return data


def department_switch(request, id):
    department = get_object_or_404(Department, pk=id)
    if request.user.has_perm('core.view_department', department):
        request.session['current_department_id'] = int(id)
    else:
        messages.error(request, 'Access forbidden')
    return redirect('index')


def handle_403(request):
    print 'aaaaaaaa'
    messages.error(request, 'Access forbidden')
    return redirect('index')