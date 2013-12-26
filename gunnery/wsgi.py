"""
WSGI config for gunnery project.

It exposes the WSGI callable as a modulelevel variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gunnery.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# if dev
# pip install uwsgi inside virtualenv!!!
import uwsgi
from uwsgidecorators import timer
from django.utils import autoreload

@timer(3)
def change_code_gracefull_reload(sig):
    if autoreload.code_changed():
        uwsgi.reload()