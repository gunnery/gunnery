from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from core.views import get_common_page_data
from task.models import Execution 

def login(request, *args, **kwargs):
    if request.method == 'POST':
        if not request.POST.get('remember', None):
            request.session.set_expiry(0)
    return views.login(request, *args, **kwargs)

@login_required
def profile_page(request, user_id):
	data = get_common_page_data(request)
	user = get_object_or_404(User, pk=user_id)
	data['user'] = user
	data['user_executions'] = Execution.get_inline_by_user(user.id)
	return render(request, 'page/profile.html', data)

@login_required
def settings_page(request):
	data = get_common_page_data(request)
	from account.forms import account_create_form
	form = account_create_form('user_settings', request, request.user.id)
	form.fields['email'].widget.attrs['readonly'] = True
	data['form'] = form
	if request.method == 'POST':
		if form.is_valid():
			on_before_save_user(form.instance)
			form.save()
			data['user'] = form.instance
	return render(request, 'page/account_settings.html', data)

def on_before_save_user(instance):
	if len(instance.password):
		instance.set_password(instance.password)
	else:
		instance.password = User.objects.get(pk=instance.id).password
