from django.forms import *
from django.forms.widgets import Textarea, SelectMultiple
from django.forms.models import modelformset_factory
from django.db import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from .models import *
from core.forms import PageForm, TagSelect
		
class TaskForm(PageForm):
    class Meta:
        model = Task
        fields = ['name', 'description']
        widgets = {'description': Textarea(attrs={'rows': 2}) }
		
class TaskParameterForm(ModelForm):
    class Meta:
        model = TaskParameter
        fields = ['name', 'description']
        widgets = {'description': TextInput() }
		
class TaskCommandForm(ModelForm):
    class Meta:
        model = TaskCommand
        fields = ['command', 'roles']
        widgets = {'roles': TagSelect() }

		
class ExecutionForm(ModelForm):
    class Meta:
        model = Execution
        fields = ['environment']
		
class ExecutionParameterForm(ModelForm):
    class Meta:
        model = ExecutionParameter
        fields = ['name', 'value']


TaskParameterFormset = modelformset_factory(TaskParameter, 
    form=TaskParameterForm, 
    can_order=True, 
    can_delete=True, 
    extra=1)
TaskCommandFormset = modelformset_factory(TaskCommand, 
    form=TaskCommandForm, 
    can_order=True, 
    can_delete=True, 
    extra=1)