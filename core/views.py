from django.shortcuts import render
from django import template


def index(request):
	return render(request, 'page/index.html')

def application_page(request):
	return render(request, 'page/application.html')



def environment_page(request):
	return render(request, 'page/environment.html')

def environment_list():
	return



def servers_list():
	return



def task_page(request):
	return render(request, 'page/task.html')
def task_execute_page(request, task_id, environment_id=None):
	return render(request, 'page/task_execute.html')

def task_list():
	return



def execution_page(request):
	return render(request, 'page/execution.html')


def execution_list_inline():
	return

def execution_list():
	return



def modal_form(request, form, id=None):
	form_template = 'partial/'+form+'_form.html'
	return render(request, form_template, {
		'form':form, 
		'object':id != None, 
		'form_template':form_template})