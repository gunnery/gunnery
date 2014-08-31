from django.conf.urls import patterns, url

from views import modal_permissions, profile_page


urlpatterns = patterns('',
    url(r'^account/profile/(?P<user_id>[\d]+)/$', profile_page, name='profile'),
    url(r'^account/login/$', 'django.contrib.auth.views.login', {'template_name': 'page/login.html'}),
    url(r'^account/logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^account/password_reset/$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^account/password_reset_done$', 'django.contrib.auth.views.password_reset_done',
       name='password_reset_done'),
    url(r'^account/password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
       'django.contrib.auth.views.password_reset_confirm', name='password_reset_confirm'),
    url(r'^account/password_reset_complete$', 'django.contrib.auth.views.password_reset_complete',
       name='password_reset_complete'),
    url(r'^modal/permissions/(?P<group_id>[\d]+)/$', modal_permissions, name='modal_permissions'),
)