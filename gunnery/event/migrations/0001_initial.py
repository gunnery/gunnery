# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NotificationPreferences'
        db.create_table(u'event_notificationpreferences', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifications', to=orm['account.CustomUser'])),
            ('event_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('is_active', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'event', ['NotificationPreferences'])

        # Adding unique constraint on 'NotificationPreferences', fields ['user', 'event_type', 'content_type', 'object_id']
        db.create_unique(u'event_notificationpreferences', ['user_id', 'event_type', 'content_type_id', 'object_id'])

        # Adding model 'EventLog'
        db.create_table(u'event_eventlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(related_name='event_log', to=orm['core.Department'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'event', ['EventLog'])


    def backwards(self, orm):
        # Removing unique constraint on 'NotificationPreferences', fields ['user', 'event_type', 'content_type', 'object_id']
        db.delete_unique(u'event_notificationpreferences', ['user_id', 'event_type', 'content_type_id', 'object_id'])

        # Deleting model 'NotificationPreferences'
        db.delete_table(u'event_notificationpreferences')

        # Deleting model 'EventLog'
        db.delete_table(u'event_eventlog')


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
        u'core.department': {
            'Meta': {'object_name': 'Department'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'event.eventlog': {
            'Meta': {'object_name': 'EventLog'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event_log'", 'to': u"orm['core.Department']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'event.notificationpreferences': {
            'Meta': {'unique_together': "(('user', 'event_type', 'content_type', 'object_id'),)", 'object_name': 'NotificationPreferences'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'to': u"orm['account.CustomUser']"})
        }
    }

    complete_apps = ['event']