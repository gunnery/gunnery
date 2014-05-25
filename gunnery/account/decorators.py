from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.db.models import get_model
from django.utils.encoding import force_str
from django.utils.six.moves.urllib.parse import urlparse
from django.shortcuts import resolve_url
from django.utils.decorators import available_attrs


def _has_permissions(user, model_name, model_id):
    model = get_model(*model_name.split('.'))
    model.id = model_id
    if model_name == 'core.Department':
        department = model
    elif model_name == 'core.Application':
        department = model.objects.get(pk=model_id).department
    elif model_name == 'core.Server':
        department = model.objects.get(pk=model_id).environment.application.department
    elif model_name == 'task.Execution':
        department = model.objects.get(pk=model_id).environment.application.department
    elif model_name == 'core.Environment':
        department = model.objects.get(pk=model_id).application.department
    elif model_name == 'task.Task':
        department = model.objects.get(pk=model_id).application.department
    else:
        raise RuntimeError('Unknown model')
    return user.has_perm('core.view_department', department)


def _auto_resolve_parameter_name(parameters):
    if len(parameters.keys()) == 0:
        raise RuntimeError('No parameters')
    if len(parameters.keys()) > 1:
        raise RuntimeError('Too many parameters, specify parameter name for has_permissions decorator')
    return parameters.keys()[0]


def has_permissions(model, id_parameter=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not id_parameter:
                id_parameter_name = _auto_resolve_parameter_name(kwargs)
            else:
                id_parameter_name = id_parameter
            if _has_permissions(request.user, model, kwargs[id_parameter_name]):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            # urlparse chokes on lazy objects in Python 3, force to str
            resolved_login_url = force_str(
                resolve_url(settings.LOGIN_URL))
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            messages.error(request, 'Access forbidden')
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, REDIRECT_FIELD_NAME)
        return _wrapped_view
    return decorator