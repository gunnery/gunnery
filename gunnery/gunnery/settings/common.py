"""
Django settings for gunnery project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.conf import global_settings
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']
PGCRYPTO_DEFAULT_KEY = SECRET_KEY

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    #'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    'timezone_field',
    'guardian',
    'crispy_forms',
    'djcelery',
    'south',
    'core',
    'task',
    'backend',
    'account',
    'event',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
    'core.middleware.CurrentDepartment',

)

ROOT_URLCONF = 'gunnery.urls'

WSGI_APPLICATION = 'gunnery.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gunnery',
        'USER': 'gunnery',
        'PASSWORD': 'gunnery',
        'HOST': '127.0.0.1',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True
DATETIME_FORMAT = 'Y-m-d H:i'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "../static"),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

CRISPY_TEMPLATE_PACK = 'bootstrap3'
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    "core.context_processors.sidebar",
)

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"

CELERYD_TASK_TIME_LIMIT = 60 * 60
CELERYD_TASK_SOFT_TIME_LIMIT = 60 * 30

LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/'
ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: "/account/profile/%d/" % u.id,
}
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',)
AUTH_USER_MODEL = 'account.CustomUser'
ANONYMOUS_USER_ID = -1

PRIVATE_DIR = '/var/gunnery/secure'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s - %(levelname)s: %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'gunnery': {
            'handlers': ['mail_admins', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

EMAIL_NOTIFICATION = 'notification@gunnery'
DEFAULT_DEPARTMENT_GROUPS = {'admin': 'Admin', 'user': 'User'}