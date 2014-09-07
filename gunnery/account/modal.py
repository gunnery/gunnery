from django.contrib.auth import get_user_model

from core.modal import BaseModal, ModalPermissionException
from account.models import DepartmentGroup
from core.models import Department
from .forms import account_create_form, UserForm, DepartmentGroupForm, UserSystemForm


_user = get_user_model()


class BaseAccountModal(BaseModal):

    def get_form_creator(self):
        return account_create_form

    def _on_form_create_user(self):
        if not self.form.instance.id:
            self.form.fields['password'].required = True
        if self.request.user.is_superuser:
            self.form.fields['groups'].department_prefix = True
            groups = DepartmentGroup.objects.all()
        else:
            groups = DepartmentGroup.objects.filter(department_id = self.request.current_department_id)

        self.form.set_groups(groups)


class UserModal(BaseAccountModal):
    form = UserForm
    form_name = 'user'

    def permission_check(self, action):
        if not self.request.user.has_perm('core.change_department', Department(id=self.request.current_department_id)):
            raise ModalPermissionException

    def on_form_create(self):
        self._on_form_create_user()

    def on_view(self):
        self.data['model_name'] = 'User'

    def on_before_save(self):
        instance = self.form.instance
        instance.username = instance.email
        if len(instance.password):
            instance.set_password(instance.password)
        else:
            instance.password = _user.objects.get(pk=instance.id).password


class UsersystemModal(BaseAccountModal):
    form = UserSystemForm
    form_name = 'usersystem'

    def permission_check(self, action):
        if not self.request.user.is_superuser:
            raise ModalPermissionException

    def on_form_create(self):
        self._on_form_create_user()


class GroupModal(BaseAccountModal):
    form = DepartmentGroupForm
    form_name = 'group'

    def permission_check(self, action):
        if not self.request.user.has_perm('core.change_department', Department(id=self.request.current_department_id)):
            raise ModalPermissionException

    def on_before_save(self):
        self.form.instance.department_id = self.request.current_department_id

    def on_create(self):
        DepartmentGroup.assign_department_perms(self.instance, Department(id=self.request.current_department_id))

