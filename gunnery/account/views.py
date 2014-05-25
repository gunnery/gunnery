from django.contrib.auth import views
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render

from core.views import get_common_page_data
from task.models import Execution
from core.models import Department


def login(request, *args, **kwargs):
    if request.method == 'POST':
        if not request.POST.get('remember', None):
            request.session.set_expiry(0)
    return views.login(request, *args, **kwargs)


@login_required
def profile_page(request, user_id):
    data = get_common_page_data(request)
    user = get_object_or_404(get_user_model(), pk=user_id)
    data['user_profile'] = user
    data['user_executions'] = Execution.get_inline_by_user(user.id)
    return render(request, 'page/profile.html', data)


def on_before_save_user(instance):
    if len(instance.password):
        instance.set_password(instance.password)
    else:
        instance.password = get_user_model().objects.get(pk=instance.id).password

@user_passes_test(lambda u: u.is_superuser)
def modal_permissions(request, user_id):
    user = get_object_or_404(get_user_model(), pk=user_id)
    data = get_common_page_data(request)
    data['user'] = user
    data['form_template'] = 'partial/permissions_form.html'
    data['model_name'] = '%s permissions' % user.name
    data['is_new'] = False
    data['no_delete'] = True
    data['request_path'] = request.path

    data['departments'] = Department.objects.all()

    from core.models import Application, Environment
    from task.models import Task

    models = {
        'department': Department,
        'application': Application,
        'environment': Environment,
        'task': Task,
    }
    if request.method == 'POST':
        from guardian.models import UserObjectPermission
        from guardian.shortcuts import assign_perm

        UserObjectPermission.objects.filter(user_id=user.id).delete()
        for name, value in request.POST.items():
            key = name.split('_')
            if len(key) == 3 and value == 'on':
                action, model, pk = key
                assign_perm('%s_%s' % (action, model), user, models[model].objects.get(pk=pk))
        return render(request, data['form_template'], data)
    else:
        return render(request, 'partial/modal_form.html', data)
