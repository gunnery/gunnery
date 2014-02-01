from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^user/login/$', 'django.contrib.auth.views.login', {'template_name': 'page/login.html'}),
    url(r'^user/logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
)