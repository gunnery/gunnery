from timezone_field import TimeZoneFormField
from django.forms import BooleanField, CharField, PasswordInput, ModelMultipleChoiceField
from django.contrib.auth import get_user_model

from core.forms import ModalForm, create_form
from .models import DepartmentGroup
from core.forms import TagSelect

_user = get_user_model()


class DepartmentGroupForm(ModalForm):
    local_name = CharField(label='Name')

    class Meta:
        model = DepartmentGroup
        fields = ['local_name']

class UserGroupsField(ModelMultipleChoiceField):
    widget = TagSelect
    department_prefix = False

    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = None
        super(UserGroupsField, self).__init__(*args, **kwargs)
        self.help_text = ''

    def label_from_instance(self, obj):
        if self.department_prefix:
            return "%s %s" % (obj.department.name, obj.local_name)
        else:
            return obj.local_name


class UserForm(ModalForm):
    email = CharField(required=True)
    password = CharField(widget=PasswordInput(render_value=False), required=False, min_length=8)
    name = CharField(label='Name')
    groups = UserGroupsField()

    def set_groups(self, groups):
        self.fields['groups'].queryset = groups

    class Meta:
        model = _user
        fields = ['email', 'password', 'name', 'groups']


class UserSystemForm(UserForm):
    is_superuser = BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(UserSystemForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'email',
            'password',
            'name',
            'groups',
            'is_superuser']

    class Meta:
        model = _user
        fields = ['email', 'password', 'name', 'groups', 'is_superuser']


class UserProfileForm(ModalForm):
    email = CharField(required=True)
    name = CharField(label='Name')
    timezone = TimeZoneFormField()

    class Meta:
        model = _user
        fields = ['email', 'name', 'timezone']


class UserPasswordForm(ModalForm):
    password = CharField(widget=PasswordInput(render_value=False), required=False, min_length=8)
    password2 = CharField(widget=PasswordInput(render_value=False), required=False, min_length=8,
                          label="Repeat password")

    class Meta:
        model = _user
        fields = ['password']

    def is_valid(self):
        valid = super(UserPasswordForm, self).is_valid()
        if not valid:
            return valid
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            self._errors['not_match'] = 'Passwords do not match'
            return False
        return True


def account_create_form(name, request, id, args={}):
    form_objects = {
        'group': DepartmentGroupForm,
        'user': UserForm,
        'usersystem': UserSystemForm,
        'user_profile': UserProfileForm,
        'user_password': UserPasswordForm
    }
    form = create_form(form_objects, name, request.POST, id, args)
    return form