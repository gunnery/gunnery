from django.contrib.auth import get_user_model

from core.modal import BaseModal
from .forms import account_create_form, UserForm


_user = get_user_model()


class Modal(BaseModal):
    definitions = {
        'user': {
            'form': UserForm,
            'parent': None
        }
    }

    def get_form_creator(self):
        return account_create_form

    def on_form_create_user(self):
        if not self.form.instance.id:
            self.form.fields['password'].required = True

    def on_update_user(self):
        self.instance.save()

    def on_before_save_user(self):
        instance = self.form.instance
        instance.username = instance.email
        if len(instance.password):
            instance.set_password(instance.password)
        else:
            instance.password = _user.objects.get(pk=instance.id).password

    def on_create_user(self):
        self.instance.save()
        from guardian.shortcuts import assign_perm
        from core.models import Department
        assign_perm('core.view_department', self.instance, Department(id=self.request.current_department_id))

    def on_view_user(self):
        self.data['model_name'] = 'User'