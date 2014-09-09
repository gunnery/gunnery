from django.forms import ModelForm, ModelMultipleChoiceField, CharField
from django.forms.widgets import Textarea, SelectMultiple, HiddenInput, TextInput, PasswordInput
from django.http import Http404

from crispy_forms.helper import FormHelper

from .models import (
    Application, Department, Environment, Server, ServerRole)


class ModalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-7'
        self.helper.label_size = ' col-sm-offset-3'


class PageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-7'


class TagSelect(SelectMultiple):
    def __init__(self, *args, **kwargs):
        super(TagSelect, self).__init__(*args, **kwargs)
        self.attrs = {'class': 'chosen-select', 'data-placeholder': ' '}
        if 'attrs' in kwargs and 'data-placeholder' in kwargs['attrs']:
            self.attrs['data-placeholder'] = kwargs['attrs']['data-placeholder']


class ServerRoleField(ModelMultipleChoiceField):
    widget = TagSelect

    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = ServerRole.objects.all()
        super(ServerRoleField, self).__init__(*args, **kwargs)
        self.help_text = ''


class ApplicationForm(ModalForm):
    class Meta:
        model = Application
        fields = ['name']
        widgets = {'description': Textarea(attrs={'rows': 2})}


class EnvironmentForm(ModalForm):
    class Meta:
        model = Environment
        fields = ['name', 'application']
        widgets = {'description': Textarea(attrs={'rows': 2}),
                   'application': HiddenInput()}


class ServerForm(ModalForm):
    roles = ServerRoleField()
    password = CharField(required=False, widget=PasswordInput)
    user = CharField(widget=TextInput(attrs={'autocomplete': 'off'}))

    class Meta:
        model = Server
        fields = ['environment', 'name', 'roles', 'host', 'port', 'user', 'method']
        widgets = {'roles': TagSelect(),
                   'environment': HiddenInput(),
                   'password': TextInput()}


class ServerRoleForm(ModalForm):
    class Meta:
        model = ServerRole
        fields = ['name']


class DepartmentForm(ModalForm):
    class Meta:
        model = Department
        fields = ['name']


def create_form(form_objects, name, request_data, id, args={}):
    """ Helper function for creating form object """
    if not name in form_objects:
        raise Http404()
    if id:
        instance = form_objects[name].Meta.model.objects.get(pk=id)
        form = form_objects[name](request_data or None, instance=instance)
    else:
        instance = form_objects[name].Meta.model(**args)
        form = form_objects[name](request_data or None, instance=instance)
    return form


def core_create_form(name, request, id, args={}):
    """ Helper function for creating core form object """
    form_objects = {
        'application': ApplicationForm,
        'environment': EnvironmentForm,
        'server': ServerForm,
        'serverrole': ServerRoleForm,
        'department': DepartmentForm
    }
    return create_form(form_objects, name, request.POST, id, args)
