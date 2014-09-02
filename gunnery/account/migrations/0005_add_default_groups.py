# -*- coding: utf-8 -*-
from django.conf import settings
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    def __init__(self):
        self.orm = None

    def forwards(self, orm):
        "Write your forwards methods here."
        self.orm = orm
        for department in orm['core.Department'].objects.all():
            self.on_create_department(department)
        for application in orm['core.Application'].objects.all():
            self.on_create_application(application)
        for environment in orm['core.Environment'].objects.all():
            self.on_create_environment(environment)
        for task in orm['task.Task'].objects.all():
            self.on_create_task(task)

        self.assign_users_to_groups()

    def assign_users_to_groups(self):
        for user in self.orm.CustomUser.objects.all():
            if user.is_superuser:
                continue
            for department in self.orm['core.Department'].objects.all():
                if self.has_perm(user, 'core.view_department', department):
                    user.groups.add(self.orm.DepartmentGroup.objects.get(department=department, system_name='user'))
                    user.save()

    def on_create_department(self, instance):
        for system_name, group_name in settings.DEFAULT_DEPARTMENT_GROUPS.items():
            group, created = self.orm.DepartmentGroup.objects.get_or_create(department=instance,
                                             local_name=group_name,
                                             name="%s_%s" % (instance.id, group_name),
                                             system_name=system_name)
            if created:
                group.save()
            self.assign_perm('core.view_department', group, instance)
            if system_name == 'admin':
                self.assign_perm('core.change_department', group, instance)

    def on_create_application(self, instance):
        self._assign_default_perms('core', 'application', instance.department, instance)

    def on_create_environment(self, instance):
        self._assign_default_perms('core', 'environment', instance.application.department, instance)

    def on_create_task(self, instance):
        self._assign_default_perms('task', 'task', instance.application.department, instance)

    def _assign_default_perms(self, app, model, department, instance):
        groups = self.orm.DepartmentGroup.objects.filter(department=department, system_name__in=['user', 'admin'])
        for group in groups:
            for action in ['view', 'execute']:
                self.assign_perm('%s.%s_%s' % (app, action, model), group, instance)
            if group.system_name == 'admin':
                self.assign_perm('%s.%s_%s' % (app, 'change', model), group, instance)

    def assign_perm(self, perm, group, instance):
        content_type, permission = self.parse_perm(perm)
        group_permission, created = self.orm['guardian.groupobjectpermission'].objects.get_or_create(
                                        permission=permission,
                                        content_type=content_type,
                                        group=group,
                                        object_pk=instance.id)
        if created:
            group_permission.save()

    def parse_perm(self, perm):
        app, perm = perm.split('.')
        action, model = perm.split('_')
        content_type = self.orm['contenttypes.ContentType'].objects.get(app_label=app, model=model)
        permission = self.orm['auth.permission'].objects.get(codename='%s_%s'%(action, model))
        return content_type, permission

    def has_perm(self, user, perm, obj):
        content_type, permission = self.parse_perm(perm)
        results = self.orm['guardian.userobjectpermission'].objects.filter(permission=permission,
                                                                          content_type=content_type,
                                                                          user_id=user.id,
                                                                          object_pk=obj.id).count()
        return bool(results)


    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'account.customuser': {
            'Meta': {'object_name': 'CustomUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '254'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'timezone': ('timezone_field.fields.TimeZoneField', [], {'default': "'UTC'"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'account.departmentgroup': {
            'Meta': {'ordering': "['name']", 'object_name': 'DepartmentGroup', '_ormbases': [u'auth.Group']},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groups'", 'to': u"orm['core.Department']"}),
            u'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'local_name': ('django.db.models.fields.CharField', [], {'max_length': '124'}),
            'system_name': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.department': {
            'Meta': {'ordering': "['name']", 'object_name': 'Department'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'guardian.groupobjectpermission': {
            'Meta': {'unique_together': "([u'group', u'permission', u'object_pk'],)", 'object_name': 'GroupObjectPermission'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Permission']"})
        },
        u'guardian.userobjectpermission': {
            'Meta': {'unique_together': "([u'user', u'permission', u'object_pk'],)", 'object_name': 'UserObjectPermission'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_pk': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Permission']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['account.CustomUser']"})
        },
        u'core.application': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('department', 'name'),)", 'object_name': 'Application'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'applications'", 'to': u"orm['core.Department']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'core.environment': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('application', 'name'),)", 'object_name': 'Environment'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environments'", 'to': u"orm['core.Application']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_production': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'core.server': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('environment', 'name'),)", 'object_name': 'Server'},
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'servers'", 'to': u"orm['core.Environment']"}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '22'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'servers'", 'symmetrical': 'False', 'to': u"orm['core.ServerRole']"}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'core.serverauthentication': {
            'Meta': {'object_name': 'ServerAuthentication'},
            'password': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'server': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Server']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'core.serverrole': {
            'Meta': {'unique_together': "(('department', 'name'),)", 'object_name': 'ServerRole'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'serverroles'", 'to': u"orm['core.Department']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'task.task': {
            'Meta': {'unique_together': "(('application', 'name'),)", 'object_name': 'Task'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': u"orm['core.Application']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
    }

    complete_apps = ['account']
    symmetrical = True
