from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^application/(?P<application_id>[\d]+)/task/$', task_form_page, name='task_add_form_page'),
    url(r'^task/(?P<task_id>[\d]+)/execute/(?P<environment_id>[\d]+)/$', task_execute_page, name='task_execute_page'),
    url(r'^task/(?P<task_id>[\d]+)/execute/$', task_execute_page, name='task_execute_page'),
    url(r'^task/(?P<task_id>[\d]+)/edit/$', task_form_page, name='task_form_page'),
    url(r'^task/(?P<task_id>[\d]+)/delete/$', task_delete, name='task_delete'),
    url(r'^task/(?P<task_id>[\d]+)/$', task_page, name='task_page'),
    url(r'^execution/(?P<execution_id>[\d]+)/$', execution_page, name='execution_page'),
    url(r'^execution/live_log/(?P<execution_id>[\d]+)/(?P<last_id>[\d]+)/$', live_log, name='live_log'),

    url(r'^log/(?P<model_name>[a-z_]+)/(?P<id>[\d]+)/$', log_page, name='log'),
)