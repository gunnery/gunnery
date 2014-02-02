from django.conf.urls import patterns, url, include
from views import *

urlpatterns = patterns('',
    url(r'^account/profile/(?P<user_id>[\d]+)/$', profile, name='profile'),
    url(r'^account/login/$', 'django.contrib.auth.views.login', {'template_name': 'page/login.html'}),
    url(r'^account/logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
)