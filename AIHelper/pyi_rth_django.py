import inspect
import os
import sys

import django.core.management
import django.utils.autoreload

#PROJECT_PATH = os.path.realpath(os.path.dirname(inspect.getfile(inspect.currentframe())))
#sys.path.append(os.path.join(PROJECT_PATH, 'apps'),)

def _get_commands():
    commands = {
         'clearsessions': 'django.contrib.sessions',
         'startcomputetask': 'manager',
         'runserver': 'django.core'
    }
    return commands

_old_restart_with_reloader = django.utils.autoreload.restart_with_reloader

def _restart_with_reloader(*args):
    a0 = sys.argv.pop(0)
    try:
        return _old_restart_with_reloader(*args)
    finally:
        sys.argv.insert(0, a0)

django.core.management.get_commands = _get_commands
django.utils.autoreload.restart_with_reloader = _restart_with_reloader