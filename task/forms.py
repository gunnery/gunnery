from django.forms import *
from django.forms.widgets import Textarea, SelectMultiple, HiddenInput
from django.forms.models import modelformset_factory
from django.db import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from .models import *
from core.forms import PageForm, TagSelect
		
class TaskForm(PageForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'application']
        widgets = {'description': Textarea(attrs={'rows': 2}),
            'application': HiddenInput() }
		
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

from django.forms.models import BaseModelFormSet
from django.core.exceptions import ValidationError
class RequireFirst(BaseModelFormSet):
    def clean(self, *args, **kwargs):
        super(RequireFirst, self).clean()
        has_one = False
        for form in self.forms:
            if 'command' in form.cleaned_data and form.cleaned_data['DELETE']==False :
                has_one = True
        if not has_one:
            raise ValidationError('At least one command must be specified')

TaskParameterFormset = modelformset_factory(TaskParameter, 
    form=TaskParameterForm, 
    can_order=True, 
    can_delete=True, 
    extra=1)
TaskCommandFormset = modelformset_factory(TaskCommand, 
    form=TaskCommandForm, 
    can_order=True, 
    can_delete=True, 
    extra=2,
    formset=RequireFirst)