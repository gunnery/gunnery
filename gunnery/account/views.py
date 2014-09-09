from django.contrib.auth import views
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import json
from account.models import DepartmentGroup

from task.models import Execution
from core.models import Department


def login(request, *args, **kwargs):
    if request.method == 'POST':
        if not request.POST.get('remember', None):
            request.session.set_expiry(0)
    return views.login(request, *args, **kwargs)


@login_required
def profile_page(request, user_id):
    data = {}
    user = get_object_or_404(get_user_model(), pk=user_id)
    data['user_profile'] = user
    data['user_executions'] = Execution.get_inline_by_user(user.id)
    return render(request, 'page/profile.html', data)


def on_before_save_user(instance):
    if len(instance.password):
        instance.set_password(instance.password)
    else:
        instance.password = get_user_model().objects.get(pk=instance.id).password

def modal_permissions(request, group_id):
    group = get_object_or_404(DepartmentGroup, pk=group_id)
    department = Department.objects.get(pk=request.current_department_id)
    if group.department_id != department.id:
        return
    if not request.user.has_perm('core.change_department', department):
        return
    data = {}
    data['group'] = group
    data['form_template'] = 'partial/permissions_form.html'
    data['model_name'] = '%s group permissions' % group.local_name
    data['is_new'] = False
    data['no_delete'] = True
    data['request_path'] = request.path
    data['applications'] = department.applications

    from core.models import Application, Environment
    from task.models import Task

    models = {
        'department': Department,
        'application': Application,
        'environment': Environment,
        'task': Task,
    }
    if request.method == 'POST':
        from guardian.models import GroupObjectPermission
        from guardian.shortcuts import assign_perm

        GroupObjectPermission.objects.filter(group_id=group.id).delete()
        assign_perm('core.view_department', group, group.department)
        for name, value in request.POST.items():
            key = name.split('_')
            if len(key) == 3 and value == 'on':
                action, model, pk = key
                assign_perm('%s_%s' % (action, model), group, models[model].objects.get(pk=pk))
        return HttpResponse(json.dumps({'status': True}), content_type="application/json")
    else:
        return render(request, 'partial/modal_form.html', data)

