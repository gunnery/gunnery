from django.conf.urls import patterns, url
from .views.main import *
from .views.modal import *
from .views.task import *

urlpatterns = patterns('',
    url(r'^$', index, name='index'),
    url(r'^application/(?P<application_id>[\d]+)/task/$', task_form_page, name='task_add_form_page'),
    url(r'^application/(?P<application_id>[\d]+)/$', application_page, name='application_page'),
    url(r'^environment/(?P<environment_id>[\d]+)/$', environment_page, name='environment_page'),
    url(r'^task/(?P<task_id>[\d]+)/execute/(?P<environment_id>[\d]+)/$', task_execute_page, name='task_execute_page'),
    url(r'^task/(?P<task_id>[\d]+)/execute/$', task_execute_page, name='task_execute_page'),
    url(r'^task/(?P<task_id>[\d]+)/edit/$', task_form_page, name='task_form_page'),
    url(r'^task/(?P<task_id>[\d]+)/$', task_page, name='task_page'),
    url(r'^execution/(?P<execution_id>[\d]+)/$', execution_page, name='execution_page'),

    url(r'^modal_form/(?P<form_name>[a-z_]+)/$', modal_form, name='modal_form'),
    url(r'^modal_form/(?P<form_name>[a-z_]+)/(?P<id>\d+)/$', modal_form, name='modal_form'),
    url(r'^modal_form/(?P<parent_name>[a-z_]+)/(?P<parent_id>\d+)/(?P<form_name>[a-z_]+)/(?P<id>\d+)?/?$', modal_form, name='modal_form'),
    url(r'^modal_delete/(?P<model_name>[a-z_]+)/(?P<id>\d+)/$', modal_delete, name='modal_delete'),

    url(r'^settings/', settings_page, name='settings_page'),
)