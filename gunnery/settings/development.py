from .common import *

DEBUG = True

TEMPLATE_DEBUG = True

INSTALLED_APPS += (
	'debug_toolbar',
)

CELERYD_TASK_TIME_LIMIT=60*5
CELERYD_TASK_SOFT_TIME_LIMIT=60*1

from fnmatch import fnmatch
class glob_list(list):
    def __contains__(self, key):
        for elt in self:
            if fnmatch(key, elt): return True
        return False
INTERNAL_IPS = glob_list(['127.0.0.1', '10.0.*.*'])
