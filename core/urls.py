from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^application/', views.application_page, name='application_page'),
    url(r'^environment/', views.environment_page, name='environment_page'),
    url(r'^task/(?P<task_id>[\d]+)/execute/(?P<environment_id>[\d]+)', views.task_execute_page, name='task_execute_page'),
    url(r'^task/(?P<task_id>[\d]+)/execute/', views.task_execute_page, name='task_execute_page'),
    url(r'^task/', views.task_page, name='task_page'),
    url(r'^execution/', views.execution_page, name='execution_page'),

    url(r'^modal_form/(?P<form>[a-z_]+)/$', views.modal_form, name='modal_form'),
    url(r'^modal_form/(?P<form>[a-z_]+)/(?P<id>\d+)/$', views.modal_form, name='modal_form'),
)