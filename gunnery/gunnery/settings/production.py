from .common import *
ENVIRONMENT = 'production'

EMAIL_USE_TLS = True
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25

DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console_error': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console_error'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}