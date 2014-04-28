import json

from django.http import Http404, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render

from guardian.shortcuts import get_objects_for_user

from backend.tasks import TestConnectionTask
from .models import Application, Department, Environment, Server, ServerRole


def get_common_page_data(request):
    data = {}
    data['departments'] = get_objects_for_user(request.user, 'core.view_department')
    # data['application_list_sidebar'] = get_objects_for_user(request.user, 'core.view_application'). \
    #     filter(department_id=request.current_department_id).prefetch_related('environments')
    data['application_list_sidebar'] = Application.objects.filter(department_id=request.current_department_id).\
        prefetch_related('environments').order_by('name')
    data['current_department_id'] = request.current_department_id
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
    data['application'] = get_object_or_404(Application, pk=application_id)
    return render(request, 'page/application.html', data)


@login_required
def environment_page(request, environment_id):
    data = get_common_page_data(request)
    data['environment'] = get_object_or_404(Environment, pk=environment_id)
    data['servers'] = list(Server.objects.filter(environment_id=environment_id).prefetch_related('roles'))
    return render(request, 'page/environment.html', data)


@login_required
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
def help_page(request):
    data = get_common_page_data(request)
    return render(request, 'page/help.html', data)


@login_required
def settings_page(request, section='user', subsection='profile'):
    data = get_common_page_data(request)
    data['section'] = section
    data['subsection'] = subsection
    handler = '_settings_%s_%s' % (section, subsection)
    if section == 'system' and request.user.is_staff is not True:
        return redirect('index')
    if handler in globals():
        data = globals()[handler](request, data)
    else:
        raise Http404
    return render(request, 'page/settings.html', data)


def _settings_user_profile(request, data):
    data['subsection_template'] = 'partial/account_profile.html'
    from account.forms import account_create_form
    form = account_create_form('user_profile', request, request.user.id)
    form.fields['email'].widget.attrs['readonly'] = True
    data['form'] = form
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['user'] = form.instance
    return data


def _settings_user_password(request, data):
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
    data['users'] = get_users_with_perms(department).order_by('name')
    return data


def _settings_department_serverroles(request, data):
    data['subsection_template'] = 'partial/serverrole_list.html'
    data['serverroles'] = ServerRole.objects.filter(department_id=request.current_department_id)
    data['empty'] = not bool(data['serverroles'].count())
    return data


def _settings_system_departments(request, data):
    data['subsection_template'] = 'partial/department_list.html'
    data['departments'] = Department.objects.all()
    return data


def _settings_system_users(request, data):
    data['subsection_template'] = 'partial/user_list.html'
    data['users'] = get_user_model().objects.order_by('name')
    return data


def department_switch(request, id):
    department = get_object_or_404(Department, pk=id)
    if request.user.has_perm('core.view_department', department):
        request.session['current_department_id'] = int(id)
    return redirect('index')
