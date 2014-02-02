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
def profile(request, user_id):
	data = get_common_page_data(request)
	user = get_object_or_404(User, pk=user_id)
	data['user'] = user
	data['user_executions'] = Execution.objects.filter(user_id=user.id).order_by('-time_created')[:3]
	return render(request, 'page/profile.html', data)