import json

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from core.models import Department, Application, Environment, Server

from forms import (
    ApplicationForm, core_create_form, DepartmentForm, EnvironmentForm,
    ServerForm, ServerRoleForm)
from .views import ServerRole


class ModalPermissionException(Exception):
    pass


def modal_form(request, form_name, id=None, parent_name=None, parent_id=None, app=None):
    try:
        return _get_app_modal(app, form_name)(id, parent_id).render(request)
    except ModalPermissionException:
        return HttpResponse({'status': False, 'message':'Access forbidden'}, content_type="application/json", status=403)


def modal_delete(request, form_name, id, app='core'):
    try:
        return _get_app_modal(app, form_name)(id).delete(request)
    except ModalPermissionException:
        return HttpResponse({'status': False, 'message':'Access forbidden'}, content_type="application/json", status=403)


def _get_app_modal(app, form_name):
    if not app:
        app = 'core'
    if app in settings.INSTALLED_APPS:
        obj = __import__(app, fromlist=['modal']).modal
        try:
            obj = getattr(obj, '%sModal' % form_name.title())
        except AttributeError:
            raise Http404()
    else:
        raise Http404()
    return obj


class BaseModal(object):
    """ Base class for modal dialog boxes

    Defines associated types, their models and forms
    """
    form = None
    form_name = ''
    parent = None
    def __init__(self, id=None, parent_id=None):
        self.id = id
        self.parent_id = parent_id
        self.data = {'status': True, 'action': 'reload'}
        self.form = None
        self.instance = None
        self.request = None
        self.is_new = False

    def create_form(self):
        """ Returns form object """
        self.form = self.get_form_creator()(self.form_name, self.request, self.id, self.get_form_args())
        self.on_form_create()

    def get_form_args(self):
        args = {}
        if self.parent:
            args[self.parent] = self.parent_id
        return args

    def _permission_check(self):
        if self.is_new:
            self.permission_check('create')
        else:
            self.permission_check('change')

    def render(self, request):
        """ Returns rendered view """
        self.request = request
        self.create_form()
        form_template = 'partial/' + self.form_name + '_form.html'
        self.is_new = not bool(self.id)
        self._permission_check()
        if request.method == 'POST':
            template = form_template
            result = self.save_form()
            if result:
                return result
        else:
            template = 'partial/modal_form.html'
        self.data = {
            'form': self.form,
            'form_template': form_template,
            'is_new': self.is_new,
            'instance': self.form.instance,
            'model_name': self.form.Meta.model.__name__,
            'request_path': request.path
        }
        self.on_view()
        return render(request, template, self.data)

    def save_form(self):
        if self.form.is_valid():
            try:
                self.on_before_save()
                self.instance = self.form.save()

                if self.is_new:
                    self.on_create()
                    self.message('Created')
                else:
                    self.on_update()
                    self.message('Saved')
                return HttpResponse(json.dumps(self.data), content_type="application/json")
            except IntegrityError as e:
                from django.forms.util import ErrorList

                errors = self.form._errors.setdefault("__all__", ErrorList())
                errors.append('Integrity error')
                errors.append(e)

    def message(self, message):
        """ Add session message
        """
        messages.success(self.request, message)

    def delete(self, request):
        """ Handles delete on modal model """
        self.request = request
        self.create_form()
        self.instance = get_object_or_404(self.form.Meta.model, pk=self.id)
        self.permission_check('delete')
        self.instance.delete()
        self.on_delete()
        self.message('Deleted')
        return HttpResponse(json.dumps(self.data), content_type="application/json")

    def permission_check(self, action):
        return True

    def on_before_save(self):
        pass

    def on_create(self):
        pass

    def on_update(self):
        pass

    def on_delete(self):
        pass

    def on_form_create(self):
        pass

    def on_view(self):
        pass


class BaseCoreModal(BaseModal):
    def get_form_creator(self):
        return core_create_form


class DepartmentModal(BaseCoreModal):
    form = DepartmentForm
    form_name = 'department'

    def permission_check(self, action):
        if not self.request.user.is_superuser:
            raise ModalPermissionException


class ServerroleModal(BaseCoreModal):
    form = ServerRoleForm
    form_name = 'serverrole'

    def permission_check(self, action):
        if not self.request.user.has_perm('core.change_department', Department(id=self.request.current_department_id)):
            raise ModalPermissionException

    def on_before_save(self):
        instance = self.form.instance
        if not instance.id:
            instance.department_id = self.request.current_department_id


class ApplicationModal(BaseCoreModal):
    form = ApplicationForm
    form_name = 'application'

    def permission_check(self, action):
        if action == 'create':
            if not self.request.user.has_perm('core.change_department', Department(id=self.request.current_department_id)):
                raise ModalPermissionException
        elif not self.request.user.has_perm('core.change_application', Application(id=self.id)):
            raise ModalPermissionException

    def on_before_save(self):
        instance = self.form.instance
        if not instance.id:
            instance.department_id = self.request.current_department_id

    def on_create(self):
        self.data['action'] = 'redirect'
        self.data['target'] = self.instance.get_absolute_url()

    def on_delete(self):
        self.data['action'] = 'redirect'
        self.data['target'] = reverse('index')


class EnvironmentModal(BaseCoreModal):
    form = EnvironmentForm
    form_name = 'environment'
    parent = 'application_id'

    def permission_check(self, action):
        if action == 'create':
            if not self.request.user.has_perm('core.change_application', Application(id=self.parent_id)):
                raise ModalPermissionException
        elif not self.request.user.has_perm('core.change_environment', Environment(id=self.id)):
            raise ModalPermissionException

    def on_delete(self):
        self.data['action'] = 'redirect'
        self.data['target'] = self.instance.application.get_absolute_url()


class ServerModal(BaseCoreModal):
    form = ServerForm
    form_name = 'server'
    parent = 'environment_id'

    def permission_check(self, action):
        if self.parent_id:
            environment = Environment(id=self.parent_id)
        else:
            server = get_object_or_404(self.form.Meta.model, pk=self.id)
            environment = server.environment
        if not self.request.user.has_perm('core.change_environment', environment):
            raise ModalPermissionException

    def on_view(self):
        from backend.tasks import read_public_key
        try:
            self.data['pubkey'] = read_public_key.delay(self.form.instance.environment_id).get()
        except Exception as e:
            self.data['pubkey'] = 'Couldn\'t load'
        if not self.is_new:
            self.form.fields['password'].help_text = "Leave blank if not changing"

    def on_create(self):
        self.on_update()

    def on_update(self):
        from backend.tasks import SaveServerAuthenticationData
        SaveServerAuthenticationData().delay(self.instance.id, password=self.form.cleaned_data['password']).get()

    def on_form_create(self):
        self.form.fields['roles'].queryset = ServerRole.objects.filter(department_id=self.request.current_department_id)