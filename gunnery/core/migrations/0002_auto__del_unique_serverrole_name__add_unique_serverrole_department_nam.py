# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'ServerRole', fields ['name']
        db.delete_unique(u'core_serverrole', ['name'])

        # Adding unique constraint on 'ServerRole', fields ['department', 'name']
        db.create_unique(u'core_serverrole', ['department_id', 'name'])


    def backwards(self, orm):
        # Removing unique constraint on 'ServerRole', fields ['department', 'name']
        db.delete_unique(u'core_serverrole', ['department_id', 'name'])

        # Adding unique constraint on 'ServerRole', fields ['name']
        db.create_unique(u'core_serverrole', ['name'])


    models = {
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
            'Meta': {'unique_together': "(('department', 'name'),)", 'object_name': 'ServerRole'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'serverroles'", 'to': u"orm['core.Department']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['core']