from django.forms import ModelForm, TextInput, ValidationError
from django.forms.widgets import Textarea, HiddenInput
from django.forms.models import modelformset_factory, BaseModelFormSet

from .models import (
    Execution, ExecutionParameter, Task, TaskCommand, TaskParameter, ParameterParser)
from core.forms import PageForm, TagSelect, create_form


class TaskForm(PageForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'application']
        widgets = {'description': Textarea(attrs={'rows': 2}),
                   'application': HiddenInput()}


class TaskParameterForm(ModelForm):
    class Meta:
        model = TaskParameter
        fields = ['name', 'description']
        widgets = {'description': TextInput()}

    def clean_name(self):
        data = self.cleaned_data['name']
        reserved_names = ParameterParser.global_parameters.keys()
        reserved_names.append('environment')
        if data in reserved_names:
            raise ValidationError("This name is reserved.")
        return data


class TaskCommandForm(ModelForm):
    class Meta:
        model = TaskCommand
        fields = ['command', 'roles']
        widgets = {'roles': TagSelect(attrs={'data-placeholder': 'Roles'})}


class ExecutionForm(ModelForm):
    class Meta:
        model = Execution
        fields = ['environment']


class ExecutionParameterForm(ModelForm):
    class Meta:
        model = ExecutionParameter
        fields = ['name', 'value']


class RequireFirst(BaseModelFormSet):
    def clean(self, *args, **kwargs):
        super(RequireFirst, self).clean()
        has_one = False
        for form in self.forms:
            if 'command' in form.cleaned_data and form.cleaned_data['DELETE'] == False:
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


def task_create_form(name, request, id, args={}):
    form_objects = {
        'task': TaskForm,
    }
    return create_form(form_objects, name, request.POST, id, args)
