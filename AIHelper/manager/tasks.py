from . import models
from bots import models as bots_models
from navigation import models as navigation_models
# from .views import global_cache
from bots.utilities import behaviour
from background_task import background

@background(schedule=5)
def manager_compute(global_cache):
    # global global_cache
    level_object = global_cache.level_object
    print("RUNNING TASK")
    if level_object:
        print("test")
        for bot in bots_models.Bot.objects.all():
            bot : bots_models.Bot = bot
            behaviour.compute(bot.bot_index, level_object, bots_models.Bot, bots_models.Player, navigation_models.Objective, int(bot['requested_target_id'])!=-2, int(bot['requested_target_id']))