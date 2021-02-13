from typing import Any
from django.core.management.base import BaseCommand, CommandError, CommandParser
import time

from manager.views import GlobalCache
from bots.utilities import behaviour
from bots import models as bot_models
from manager import models
from navigation import models as navigation_models

class Command(BaseCommand):
    help = "Runs compute tasks for the bots in the background"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--interval', '-i', type=float, action='store', default=2.0)
    
    def handle(self, *args: Any, **options: Any) -> Any:
        print("CTRL+C to Stop Task")
        global_cache = GlobalCache()
        while True:
            print("updating")
            currentGameManager = models.BF3GameManager.objects.first()
            if currentGameManager:
                level_object = global_cache.get_object(
                    currentGameManager.active_project_id,
                    currentGameManager.active_level_id
                )
                if level_object:
                    for bot in bot_models.Bot.objects.all():
                        behaviour.compute(bot.bot_index, level_object, bot_models.Bot, bot_models.Player, navigation_models.Objective, True, bot.overidden_target)
            else:
                print("No Game Manager found. Maybe start the game?")
            time.sleep(options['interval'])

        return None