from .common import *
ENVIRONMENT = 'test'

TEST_DISCOVER_TOP_LEVEL = BASE_DIR
TEST_DISCOVER_ROOT = BASE_DIR
TEST_DISCOVER_PATTERN = "*"

INSTALLED_APPS += (
    'django_nose',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

CELERY_ALWAYS_EAGER = True

PRIVATE_DIR = '/tmp'

import logging
south_logger = logging.getLogger('south')
south_logger.setLevel(logging.INFO)