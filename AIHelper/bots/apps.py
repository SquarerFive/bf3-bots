from django.apps import AppConfig

from .utilities import behaviour
# from bot_task_graph import *

class BotsConfig(AppConfig):
    name = 'bots'

    def ready(self):
        behaviour.global_behaviour_thread = \
        behaviour.ThreadPool(threads=2, config=behaviour.TaskPoolConfig(5.0, 1.0))
