from django.contrib.auth import get_user_model

from core.modal import BaseModal
from account.models import DepartmentGroup
from .forms import account_create_form, UserForm, DepartmentGroupForm, UserSystemForm


_user = get_user_model()


class Modal(BaseModal):
    definitions = {
        'user': {
            'form': UserForm,
            'parent': None
        },
        'user_system': {
            'form': UserSystemForm,
            'parent': None
        },
        'group': {
            'form': DepartmentGroupForm,
            'parent': None
        }
    }

    def get_form_creator(self):
        return account_create_form

    def on_form_create_user(self):
        if not self.form.instance.id:
            self.form.fields['password'].required = True
        if self.request.user.is_superuser:
            self.form.fields['groups'].department_prefix = True
            groups = DepartmentGroup.objects.all()
        else:
            groups = DepartmentGroup.objects.filter(department_id = self.request.current_department_id)

        self.form.set_groups(groups)

    def on_view_user(self):
        self.data['model_name'] = 'User'

    def on_form_create_user_system(self):
        self.on_form_create_user()

    def on_before_save_user(self):
        instance = self.form.instance
        instance.username = instance.email
        if len(instance.password):
            instance.set_password(instance.password)
        else:
            instance.password = _user.objects.get(pk=instance.id).password
    #
    # def on_update_user(self):
    #     self.instance.save()
    #
    # def on_create_user(self):
    #     self.instance.save()

    def on_before_save_group(self):
        self.form.instance.department_id = self.request.current_department_id