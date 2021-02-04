from AIHelper.celery import app
from celery import Celery
# from celery.task.schedules import crontab
# from celery.decorators import periodic_task

from celery.schedules import crontab

from bots import models
from .utilities import behaviour

from navigation import models as navigation_models
from navigation.utilities import query as navigation_query
from navigation.utilities import level

from typing import Union

# Globals [to avoid poo memory, cache it here until the level changes]
class GlobalCache:
    def __init__(self):
        self.level_model : Union[level.models.Level, None] = None
        self.level_object : Union[level.Level, None] = None
    
    def get_object(self, project_id : int, level_id : int):
        if self.level_object:
            if self.level_object.model.project_id == project_id:
                return self.level_object
        self.level_model = level.models.Level.objects.filter(project_id= project_id, level_id=level_id).first()
        self.level_object = navigation_query.decode_level(self.level_model)
        return self.level_object

    def save_object(self):
        if self.level_object:
            navigation_query.encode_level(self.level_object)

global_cache = GlobalCache()

@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # print("setup tasks")
    sender.add_periodic_task(2.0, btask.s(), name='Bot Behaviour')

@app.task
def btask():
    # print("Hello")
    #print(a)
    current_level_model = navigation_models.Level.objects.first()
    current_level = navigation_query.decode_level(current_level_model)
    for bot in models.Bot.objects.all():
        behaviour.compute(bot.bot_index, current_level, models.Bot, models.Player, navigation_models.Objective)
    
    