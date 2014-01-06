from django.forms import *
from django.forms.widgets import Textarea, SelectMultiple, HiddenInput
from .models import *
from django.db import models
from crispy_forms.helper import FormHelper
from django.forms.models import modelformset_factory
from crispy_forms.layout import *

class ModalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-7'

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
        self.attrs = {'class':'chosen-select', 'data-placeholder': ' '}
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
        fields = ['name', 'description']
        widgets = {'description': Textarea(attrs={'rows': 2}) }

class EnvironmentForm(ModalForm):
    class Meta:
        model = Environment
        fields = ['name', 'description', 'application']
        widgets = {'description': Textarea(attrs={'rows': 2}),
            'application': HiddenInput() }

class ServerForm(ModalForm):
    roles = ServerRoleField()
    class Meta:
        model = Server
        fields = ['name', 'host', 'user', 'roles', 'environment']
        widgets = {'roles': TagSelect(),
            'environment': HiddenInput() }

class ServerRoleForm(ModalForm):
    class Meta:
        model = ServerRole
        fields = ['name']
