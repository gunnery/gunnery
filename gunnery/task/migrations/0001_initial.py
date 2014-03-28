# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ("account", "0001_initial"),
    )

    def forwards(self, orm):
        # Adding model 'Task'
        db.create_table(u'task_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks', to=orm['core.Application'])),
        ))
        db.send_create_signal(u'task', ['Task'])

        # Adding unique constraint on 'Task', fields ['application', 'name']
        db.create_unique(u'task_task', ['application_id', 'name'])

        # Adding model 'TaskParameter'
        db.create_table(u'task_taskparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parameters', to=orm['task.Task'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('default_value', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'task', ['TaskParameter'])

        # Adding model 'TaskCommand'
        db.create_table(u'task_taskcommand', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='commands', to=orm['task.Task'])),
            ('command', self.gf('django.db.models.fields.TextField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'task', ['TaskCommand'])

        # Adding M2M table for field roles on 'TaskCommand'
        m2m_table_name = db.shorten_name(u'task_taskcommand_roles')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('taskcommand', models.ForeignKey(orm[u'task.taskcommand'], null=False)),
            ('serverrole', models.ForeignKey(orm[u'core.serverrole'], null=False))
        ))
        db.create_unique(m2m_table_name, ['taskcommand_id', 'serverrole_id'])

        # Adding model 'Execution'
        db.create_table(u'task_execution', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='executions', to=orm['task.Task'])),
            ('time_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('time_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='executions', to=orm['core.Environment'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='executions', to=orm['account.CustomUser'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=3)),
        ))
        db.send_create_signal(u'task', ['Execution'])

        # Adding model 'ExecutionParameter'
        db.create_table(u'task_executionparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('execution', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parameters', to=orm['task.Execution'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'task', ['ExecutionParameter'])

        # Adding model 'ExecutionCommand'
        db.create_table(u'task_executioncommand', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('execution', self.gf('django.db.models.fields.related.ForeignKey')(related_name='commands', to=orm['task.Execution'])),
            ('command', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'task', ['ExecutionCommand'])

        # Adding M2M table for field roles on 'ExecutionCommand'
        m2m_table_name = db.shorten_name(u'task_executioncommand_roles')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('executioncommand', models.ForeignKey(orm[u'task.executioncommand'], null=False)),
            ('serverrole', models.ForeignKey(orm[u'core.serverrole'], null=False))
        ))
        db.create_unique(m2m_table_name, ['executioncommand_id', 'serverrole_id'])

        # Adding model 'ExecutionCommandServer'
        db.create_table(u'task_executioncommandserver', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('execution_command', self.gf('django.db.models.fields.related.ForeignKey')(related_name='servers', to=orm['task.ExecutionCommand'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('time_start', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('return_code', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('server', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Server'])),
            ('output', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'task', ['ExecutionCommandServer'])

        # Adding model 'ExecutionLiveLog'
        db.create_table(u'task_executionlivelog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('execution', self.gf('django.db.models.fields.related.ForeignKey')(related_name='live_logs', to=orm['task.Execution'])),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('data', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'task', ['ExecutionLiveLog'])


    def backwards(self, orm):
        # Removing unique constraint on 'Task', fields ['application', 'name']
        db.delete_unique(u'task_task', ['application_id', 'name'])

        # Deleting model 'Task'
        db.delete_table(u'task_task')

        # Deleting model 'TaskParameter'
        db.delete_table(u'task_taskparameter')

        # Deleting model 'TaskCommand'
        db.delete_table(u'task_taskcommand')

        # Removing M2M table for field roles on 'TaskCommand'
        db.delete_table(db.shorten_name(u'task_taskcommand_roles'))

        # Deleting model 'Execution'
        db.delete_table(u'task_execution')

        # Deleting model 'ExecutionParameter'
        db.delete_table(u'task_executionparameter')

        # Deleting model 'ExecutionCommand'
        db.delete_table(u'task_executioncommand')

        # Removing M2M table for field roles on 'ExecutionCommand'
        db.delete_table(db.shorten_name(u'task_executioncommand_roles'))

        # Deleting model 'ExecutionCommandServer'
        db.delete_table(u'task_executioncommandserver')

        # Deleting model 'ExecutionLiveLog'
        db.delete_table(u'task_executionlivelog')


    models = {
        u'account.customuser': {
            'Meta': {'object_name': 'CustomUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '254'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
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
        u'core.application': {
            'Meta': {'unique_together': "(('department', 'name'),)", 'object_name': 'Application'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'applications'", 'to': u"orm['core.Department']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'core.department': {
            'Meta': {'object_name': 'Department'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'core.environment': {
            'Meta': {'unique_together': "(('application', 'name'),)", 'object_name': 'Environment'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environments'", 'to': u"orm['core.Application']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_production': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'core.server': {
            'Meta': {'unique_together': "(('environment', 'name'),)", 'object_name': 'Server'},
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'servers'", 'to': u"orm['core.Environment']"}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'servers'", 'symmetrical': 'False', 'to': u"orm['core.ServerRole']"}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'core.serverrole': {
            'Meta': {'object_name': 'ServerRole'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'serverroles'", 'to': u"orm['core.Department']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'task.execution': {
            'Meta': {'object_name': 'Execution'},
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'executions'", 'to': u"orm['core.Environment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'executions'", 'to': u"orm['task.Task']"}),
            'time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'time_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'executions'", 'to': u"orm['account.CustomUser']"})
        },
        u'task.executioncommand': {
            'Meta': {'object_name': 'ExecutionCommand'},
            'command': ('django.db.models.fields.TextField', [], {}),
            'execution': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commands'", 'to': u"orm['task.Execution']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.ServerRole']", 'symmetrical': 'False'})
        },
        u'task.executioncommandserver': {
            'Meta': {'object_name': 'ExecutionCommandServer'},
            'execution_command': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'servers'", 'to': u"orm['task.ExecutionCommand']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'output': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'return_code': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'server': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Server']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'task.executionlivelog': {
            'Meta': {'object_name': 'ExecutionLiveLog'},
            'data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'execution': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'live_logs'", 'to': u"orm['task.Execution']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'task.executionparameter': {
            'Meta': {'object_name': 'ExecutionParameter'},
            'execution': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parameters'", 'to': u"orm['task.Execution']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'task.task': {
            'Meta': {'unique_together': "(('application', 'name'),)", 'object_name': 'Task'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': u"orm['core.Application']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'task.taskcommand': {
            'Meta': {'object_name': 'TaskCommand'},
            'command': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'roles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'commands'", 'symmetrical': 'False', 'to': u"orm['core.ServerRole']"}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'commands'", 'to': u"orm['task.Task']"})
        },
        u'task.taskparameter': {
            'Meta': {'object_name': 'TaskParameter'},
            'default_value': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parameters'", 'to': u"orm['task.Task']"})
        }
    }

    complete_apps = ['task']