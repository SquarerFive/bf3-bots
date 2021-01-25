from bots import models

from navigation import models as navigation_models
from navigation.utilities.level import Level
from navigation.utilities.thread_pool import TaskPool, ThreadPool, TaskPoolConfig

from typing import Union, List, Tuple
from numba import njit
import math

from . import orders

# It's important to note, that these thread are still attached to the main thread. 

global_behaviour_thread : Union[ThreadPool, None] = None # ThreadPool(threads=2, config=TaskPoolConfig(10.0, 5.0))

@njit
def distance(x1 : float, y1 : float, z1 : float,  x2 : float, y2 : float, z2 : float ) -> float:
    return math.sqrt(
        math.pow(x2-x1, 2)+
        math.pow(y2-y1, 2)+
        math.pow(z2-z1, 2)
    )

def get_nearest_objective(target : models.Bot, objectives : List[navigation_models.Objective]) -> navigation_models.Objective:
    if len(objectives) == 0:
        return None
        
    target_position : Tuple[float, float, float] = (target.transform['trans']['x'], target.transform['trans']['y'], target.transform['trans']['z'])
    min_distance : float = 99999
    min_objective : Union[navigation_models.Objective, None] = objectives[0]
    
    for objective in objectives:
        objective_position : tuple = (objective.transform['trans']['x'], objective.transform['trans']['y'], objective.transform['trans']['z'])
        distance_to_objective : float = distance(*target_position, *objective_position)
        if distance_to_objective < min_distance:
            min_distance = distance_to_objective
            min_objective = objective
    # print("Min distance", min_distance)
    return min_objective

def get_target_objectives(team : int, ObjectiveModels : navigation_models.Objective) -> List[navigation_models.Objective]:
    targets = []
    objectives : List[navigation_models.Objective] = ObjectiveModels.objects.all()
    for obj in objectives:
        if obj.team != team or (obj.team==team and obj.controlled == False):
            targets.append(obj)
    return targets

# returns Tuple[BasePlayer, float]
# BasePlayer: Nearest enemy
# float: Distance to enemy
def get_nearest_enemy(target : models.Bot, enemies : List[models.BasePlayer]) -> Tuple[models.BasePlayer, float] :
    nearest_distance = math.inf
    nearest_enemy = None
    target_position : Tuple[float, float, float] = (target.transform['trans']['x'], target.transform['trans']['y'], target.transform['trans']['z'])
    
    for enemy in enemies:
        enemy_position : Tuple[float, float, float] = (enemy.transform['trans']['x'], enemy.transform['trans']['y'], enemy.transform['trans']['z'])
        distance_to_enemy : float = distance(*target_position, *enemy_position)
        if distance_to_enemy < nearest_distance and enemy.alive:
            nearest_distance = distance_to_enemy
            nearest_enemy = enemy
    
    return (nearest_enemy, nearest_distance)

def compute(bot_id : int, current_level : Level, BotModels : models.Bot, PlayerModels : models.Player, ObjectiveModels : navigation_models.Objective):
    bot = BotModels.objects.filter(bot_index=bot_id).first()
    
    objectives : List[navigation_models.Objective] = get_target_objectives(bot.team, ObjectiveModels)#navigation_models.Objective.objects.exclude(team=bot.team)
    
    closest_objective : Union[navigation_models.Objective, None] = get_nearest_objective(bot, objectives)

    enemies : List[models.BasePlayer] = list(BotModels.objects.exclude(team=bot.team)) + list(PlayerModels.objects.exclude(team=bot.team))

    closest_enemy, distance_to_enemy = get_nearest_enemy(bot, enemies)
    bot_grid_pos = current_level.transform.transform_to_grid((bot.transform['trans']['x'], bot.transform['trans']['z']))
    #print("Closest objective: ", closest_objective)
    #print("Closest enemy:", closest_enemy)
    # print("Compute", bot.action, int(orders.BotActionEnum.ATTACK), closest_objective, closest_enemy, objectives)
    if bot.action == int(orders.BotActionEnum.ATTACK):
        if closest_enemy and distance_to_enemy < 130: # TODO: change this to x within viewing angle of y 
            # print("attack enemy")
            # print('test')
            enemy_grid_pos =  current_level.transform.transform_to_grid((float(closest_enemy.transform['trans']['x']) , float(closest_enemy.transform['trans']['z'])))
            bot.target = closest_enemy.player_id
            bot.order = orders.BotOrdersEnum.ENEMY
            # bot.action = orders.BotActionEnum.ATTACK
            bot.path = current_level.astar(
                bot_grid_pos,
                enemy_grid_pos
            )
            #print("path")
            if type(bot.path ) == type(None):
                bot.path = []
            else:
                if len(bot.path) == 0:
                    bot.path = []
            bot.save()

        elif closest_objective:
            # print('no enemy, but close objective')
            bot.path = []
            bot.target = -1
            bot.order = orders.BotOrdersEnum.OBJECTIVE
            # bot.action = orders.BotActionEnum.ATTACK
            #print("closest obj: ", closest_objective.name)
            end =  current_level.transform.transform_to_grid((float(closest_objective.transform['trans']['x']) , float(closest_objective.transform['trans']['z'])))
            # print("closest objective @ grid = " ,end)
            # print("bot grid pos: ", current_level.transform.transform_to_grid((bot.transform['trans']['x'], bot.transform['trans']['z'])))
            path = current_level.astar(
                current_level.transform.transform_to_grid((bot.transform['trans']['x'], bot.transform['trans']['z'])),
                end#current_level.transform.transform_to_grid((float(closest_objective.transform['trans']['x']) , closest_objective.transform['trans']['z']))
            )
            bot.path = path
            # print("path: ", bot.path)
            bot.save()

    elif bot.action == 6:
        # print("GETIN")
        target = models.Player.objects.filter(player_id=bot.target).first() or models.Bot.objects.filter(player_id=bot.target).first()
        end =  current_level.transform.transform_to_grid((float(target.transform['trans']['x']) , float(target.transform['trans']['z'])))
        bot.path = current_level.astar(
                bot_grid_pos,
                end
            )
        if type(bot.path ) == type(None):
                bot.path = []
        else:
            if len(bot.path) == 0:
                bot.path = []
        bot.save()

    elif bot.in_vehicle == False and bot.action == 6:
        bot.action = 7

    elif bot.action == 7:
        if not bot.in_vehicle:
            bot.action = orders.BotActionEnum.ATTACK
        bot.target = -1
        bot.save()