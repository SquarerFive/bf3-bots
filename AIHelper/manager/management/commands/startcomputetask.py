from navigation.utilities.level import Level
from typing import Any
from django.core.management.base import BaseCommand, CommandError, CommandParser
import time

from manager.views import GlobalCache
from bots.utilities import behaviour
from bots import models as bot_models
from manager import models
from navigation import models as navigation_models

import math
import threading

class TaskPool:
    def __init__(self):
        self.active_interval = 0.001
        self.inactive_interval = 0.1
        self.interval = self.active_interval
        self.tasks = []
        self.should_stop = False
    
    def run_tasks(self):
        for task in self.tasks:
            task()
        self.tasks = []
    
    def start(self):
        while self.should_stop == False:
            try:
                self.interval = self.active_interval if len(self.tasks) > 0 else self.inactive_interval
                self.run_tasks()
                time.sleep(self.interval)
            except:
                print('key interrupt')
                self.should_stop = True

class ThreadPool:
    def __init__(self, num_threads = 6):
        self.threads = []
        self.pools = []

        for i in range(num_threads):
            self.pools.append(TaskPool())
        for pool in self.pools:
            self.threads.append(
                threading.Thread(target=pool.start)
            )

    def start(self):
        for thread in self.threads:
            thread.start()
    
    def stop(self):
        for pool in self.pools:
            pool.should_stop = True
    
    def enqueue(self, task):
        min_pool = None
        min_tasks = math.inf
        for pool in self.pools:
            if len(pool.tasks) < min_tasks:
                min_pool = pool 
                min_tasks = len(pool.tasks)
        min_pool.tasks.append(task)
    
    def stats(self):
        num_tasks = []
        for pool in self.pools:
            num_tasks.append(len(pool.tasks))
        return "Tasks: "+str(num_tasks)

class Command(BaseCommand):
    help = "Runs compute tasks for the bots in the background"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--interval', '-i', type=float, action='store', default=2.0)
        parser.add_argument('-g', '--grid', action='store_true', default = False)
        parser.add_argument('-cs', '--chunk_size', type=int, action='store', default = 8)
        parser.add_argument('-c', '--chunk', type=int, action='store', default = 0)
    
    def handle(self, *args: Any, **options: Any) -> Any:
        print("CTRL+C to Stop Task")
        global_cache = GlobalCache()
        thread_pool = ThreadPool()
        grid = options['grid']
        chunk_size = options['chunk_size']
        chunk = options['chunk']
        print(f"Use Grid: {grid}, Chunk Size: {chunk_size}, Chunk: {chunk}")
        # thread_pool.start()
        while True:
            
            currentGameManager : models.BF3GameManager = models.BF3GameManager.objects.first()
            if currentGameManager.reload:
                level_object = global_cache.get_object(
                    currentGameManager.active_project_id,
                    currentGameManager.active_level_id
                )
                currentGameManager.reload = False
                currentGameManager.save()
            ts = time.time()
            if currentGameManager:
                level_object = global_cache.get_object(
                    currentGameManager.active_project_id,
                    currentGameManager.active_level_id
                )
                if level_object:
                    b_array = []
                    t = []
                    bots = list(bot_models.Bot.objects.all())
                    
                    if grid:
                        end_size = ((chunk+1)*chunk_size) if ((chunk+1)*chunk_size)  < len(bots) else len(bots)-1
                        bots = bots[chunk_size*chunk:end_size]
                    for bot in bots:
                        print("Doing bot: ", bot.bot_index)
                        # thread_pool.enqueue(
                        #     # lambda : behaviour.compute(bot.bot_index, level_object, bot_models.Bot, bot_models.Player, navigation_models.Objective, True, bot.overidden_target)
                        #     lambda : behaviour.compute_model(bot, level_object, True, bot.overidden_target)
                        # )
                        try:
                            # behaviour.compute_model(bot, level_object, bot.overidden_target > -2, bot.overidden_target)
                            t.append(threading.Thread(target = lambda : behaviour.compute_model(bot, level_object, bot.overidden_target > -2, bot.overidden_target)))
                            t[-1].start()
                            b_array.append(bot)
                        except Exception as e:
                            print('Encountered Error: ', e)
                            raise(e)
                    for tr in t:
                        tr.join()
                    bot_models.Bot.objects.bulk_update(b_array, ['path', 'action', 'order', 'target', 'stuck', 'target_vehicle', 'target_vehicle_slot'])
                    # print(thread_pool.stats())
            else:
                print("No Game Manager found. Maybe start the game?")
            te = time.time()
            print("Completed task cycle in: {}s".format(te-ts))
            time.sleep(options['interval'])

        thread_pool.stop()
        return None