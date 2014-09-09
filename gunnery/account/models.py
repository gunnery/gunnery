from django.conf import settings
from django.db.models.signals import post_save
from guardian.shortcuts import assign_perm
from timezone_field import TimeZoneField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from task.models import Task


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password,
                     is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    email = models.EmailField(_('email address'), max_length=254, unique=True)
    name = models.CharField(_('first name'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    objects = CustomUserManager()
    timezone = TimeZoneField(default='UTC')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/account/profile/%d/" % self.id

    def get_full_name(self):
        if self.name:
            return self.name
        else:
            return self.email

    def get_short_name(self):
        return self.name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])


from django.contrib.auth.models import Group
from core.models import Department, Application, Environment


class DepartmentGroup(Group):
    department = models.ForeignKey(Department, related_name="groups")
    local_name = models.CharField(max_length=124)
    system_name = models.CharField(max_length=12)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        self.name = "%s_%s" % (self.department_id, self.local_name)
        super(DepartmentGroup, self).save(*args, **kwargs)

    def assign_department_perms(self, department):
        assign_perm('core.view_department', self, department)

    @staticmethod
    def on_create_department(sender, instance, created, **kwargs):
        if created:
            for system_name, group_name in settings.DEFAULT_DEPARTMENT_GROUPS.items():
                group = DepartmentGroup(department=instance, local_name=group_name, system_name=system_name)
                group.save()
                DepartmentGroup.assign_department_perms(group, instance)
                if system_name == 'admin':
                    assign_perm('core.change_department', group, instance)

    @staticmethod
    def on_create_application(sender, instance, created, **kwargs):
        if created:
            DepartmentGroup._assign_default_perms('core', 'application', instance.department, instance)

    @staticmethod
    def on_create_environment(sender, instance, created, **kwargs):
        if created:
            DepartmentGroup._assign_default_perms('core', 'environment', instance.application.department, instance)

    @staticmethod
    def on_create_task(sender, instance, created, **kwargs):
        if created:
            DepartmentGroup._assign_default_perms('task', 'task', instance.application.department, instance)

    @staticmethod
    def _assign_default_perms(app, model, department, instance):
        groups = DepartmentGroup.objects.filter(department=department, system_name__in=['user', 'admin'])
        for group in groups:
            for action in ['view', 'execute']:
                assign_perm('%s.%s_%s' % (app, action, model), group, instance)
            if group.system_name == 'admin':
                assign_perm('%s.%s_%s' % (app, 'change', model), group, instance)

    def __str__(self):
        return self.local_name


post_save.connect(DepartmentGroup.on_create_department, sender=Department)
post_save.connect(DepartmentGroup.on_create_application, sender=Application)
post_save.connect(DepartmentGroup.on_create_environment, sender=Environment)
post_save.connect(DepartmentGroup.on_create_task, sender=Task)