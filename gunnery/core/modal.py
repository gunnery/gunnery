import json

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from forms import (
    ApplicationForm, core_create_form, DepartmentForm, EnvironmentForm,
    ServerForm, ServerRoleForm)
from .views import ServerRole


def modal_form(request, form_name, id=None, parent_name=None, parent_id=None, app=None):
    return _get_app_modal(app)(form_name, id, parent_id).render(request)


def modal_delete(request, form_name, id, app='core'):
    return _get_app_modal(app)(form_name, id).delete(request)


def _get_app_modal(app):
    if app == None:
        obj = Modal
    else:
        if app in settings.INSTALLED_APPS:
            obj = __import__(app, fromlist=['modal']).modal.Modal
        else:
            raise Http404()
    return obj


class BaseModal(object):
    """ Base class for modal dialog boxes

    Defines associated types, their models and forms
    """
    definitions = {}

    def __init__(self, form_name, id=None, parent_id=None):
        self.form_name = form_name
        self.id = id
        self.parent_id = parent_id
        self.data = {'status': True, 'action': 'reload'}
        self.form = None
        self.instance = None
        self.request = None
        if form_name in self.definitions:
            self.definition = self.definitions[form_name]
        else:
            raise ValueError('Modal: Unknown form_name')

    def create_form(self):
        """ Returns form object """
        self.form = self.get_form_creator()(self.form_name, self.request, self.id, self.get_form_args())
        self.trigger_event('form_create')

    def get_form_args(self):
        args = {}
        if self.definition['parent']:
            args[self.definition['parent']] = self.parent_id
        return args

    def render(self, request):
        """ Returns rendered view """
        self.request = request
        self.create_form()
        form_template = 'partial/' + self.form_name + '_form.html'
        is_new = not bool(self.id)
        if request.method == 'POST':
            template = form_template
            if self.form.is_valid():
                try:
                    self.trigger_event('before_save')
                    self.instance = self.form.save()

                    if is_new:
                        self.trigger_event('create')
                        self.message('Created')
                    else:
                        self.trigger_event('update')
                        self.message('Saved')
                    return HttpResponse(json.dumps(self.data), content_type="application/json")
                except IntegrityError as e:
                    from django.forms.util import ErrorList

                    errors = self.form._errors.setdefault("__all__", ErrorList())
                    errors.append('Integrity error')
                    errors.append(e)

        else:
            template = 'partial/modal_form.html'
        self.data = {
            'form': self.form,
            'form_template': form_template,
            'is_new': is_new,
            'instance': self.form.instance,
            'model_name': self.form.Meta.model.__name__,
            'request_path': request.path
        }
        self.trigger_event('view')
        return render(request, template, self.data)

    def message(self, message):
        """ Add session message
        """
        messages.success(self.request, message)

    def delete(self, request):
        """ Handles delete on modal model """
        self.request = request
        self.create_form()
        self.instance = get_object_or_404(self.form.Meta.model, pk=self.id)
        self.instance.delete()
        self.trigger_event('delete')
        self.message('Deleted')
        return HttpResponse(json.dumps(self.data), content_type="application/json")

    def trigger_event(self, event):
        """ Triggers modal event """
        event = 'on_%s_%s' % (event, self.form_name)
        try:
            callback = getattr(self, event)
            callback()
        except AttributeError:
            pass


class Modal(BaseModal):
    definitions = {
        'application': {
            'form': ApplicationForm,
            'parent': None, },
        'environment': {
            'form': EnvironmentForm,
            'parent': 'application_id', },
        'server': {
            'form': ServerForm,
            'parent': 'environment_id'},
        'serverrole': {
            'form': ServerRoleForm,
            'parent': None},
        'department': {
            'form': DepartmentForm,
            'parent': None}
    }

    def get_form_creator(self):
        return core_create_form

    def on_before_save_application(self):
        instance = self.form.instance
        if not instance.id:
            instance.department_id = self.request.current_department_id

    def on_before_save_serverrole(self):
        instance = self.form.instance
        if not instance.id:
            instance.department_id = self.request.current_department_id

    def on_create_application(self):
        self.data['action'] = 'redirect'
        self.data['target'] = self.instance.get_absolute_url()

    def on_delete_application(self):
        self.data['action'] = 'redirect'
        self.data['target'] = reverse('index')

    def on_delete_environment(self):
        self.data['action'] = 'redirect'
        self.data['target'] = self.instance.application.get_absolute_url()

    def on_view_server(self):
        from backend.tasks import read_public_key
        try:
            self.data['pubkey'] = read_public_key.delay(self.form.instance.environment_id).get()
        except Exception as e:
            self.data['pubkey'] = 'Couldn\'t load'

    def on_create_server(self):
        self.on_update_server()

    def on_update_server(self):
        from backend.tasks import SaveServerAuthenticationData
        SaveServerAuthenticationData().delay(self.instance.id, password=self.form.cleaned_data['password']).get()

    def on_form_create_server(self):
        self.form.fields['roles'].queryset = ServerRole.objects.filter(department_id=self.request.current_department_id)

    def on_create_department(self):
        for serverrole in ['app', 'db', 'cache']:
            ServerRole(name=serverrole, department=self.instance).save()
