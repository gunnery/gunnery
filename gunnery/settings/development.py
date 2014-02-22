from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

INSTALLED_APPS += (
	#'debug_toolbar',
)

CELERYD_TASK_TIME_LIMIT=60*5
CELERYD_TASK_SOFT_TIME_LIMIT=60*1