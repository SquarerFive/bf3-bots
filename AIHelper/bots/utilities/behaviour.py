from inspect import trace
from navigation.utilities.transformations import transform_to_world
from bots import models

from navigation import models as navigation_models
from navigation.utilities.level import Level
from navigation.utilities.thread_pool import TaskPool, ThreadPool, TaskPoolConfig

from typing import Union, List, Tuple
from numba import njit
import math

from . import orders
import random
from numba import int32, float32

# It's important to note, that these thread are still attached to the main thread. 

global_behaviour_thread : Union[ThreadPool, None] = None # ThreadPool(threads=2, config=TaskPoolConfig(10.0, 5.0))

@njit
def distance(x1 : float, y1 : float, z1 : float,  x2 : float, y2 : float, z2 : float ) -> float:
    return math.sqrt(
        math.pow(x2-x1, 2)+
        math.pow(y2-y1, 2)+
        math.pow(z2-z1, 2)
    )

def get_nearest_objective(target : models.Bot, objectives : List[navigation_models.Objective]) -> Tuple[navigation_models.Objective, float]:
    if len(objectives) == 0:
        return None, math.inf
        
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
    return min_objective, min_distance

def get_target_objectives(team : int, ObjectiveModels : navigation_models.Objective) -> List[navigation_models.Objective]:
    targets = []
    objectives : List[navigation_models.Objective] = ObjectiveModels.objects.all()
    for obj in objectives:
        if obj.capturable:
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
    if nearest_enemy != None and target != None:
        if abs(target.transform['trans']['y'] - nearest_enemy.transform['trans']['y']) > 5:
            nearest_enemy = None
    return (nearest_enemy, nearest_distance)

def compute(bot_id : int, current_level : Level, BotModels : models.Bot, PlayerModels : models.Player, ObjectiveModels : navigation_models.Objective, override_target = False, override_target_id = -2):
    bot : BotModels = BotModels.objects.filter(bot_index=bot_id).first()
    
    objectives : List[navigation_models.Objective] = get_target_objectives(bot.team, ObjectiveModels)#navigation_models.Objective.objects.exclude(team=bot.team)
    
    closest_objective, distance_to_objective = get_nearest_objective(bot, objectives)

    enemies : List[models.BasePlayer] = list(BotModels.objects.exclude(team=bot.team)) + list(PlayerModels.objects.exclude(team=bot.team))

    closest_enemy, distance_to_enemy = get_nearest_enemy(bot, enemies)
    bot_grid_pos = current_level.transform.transform_to_grid((bot.transform['trans']['x'], bot.transform['trans']['z']))
    #print("Closest objective: ", closest_objective)
    #print("Closest enemy:", closest_enemy)
    # print("Compute", bot.action, int(orders.BotActionEnum.ATTACK), closest_objective, closest_enemy, objectives)
    if bot.alive:
        if bot.action == int(orders.BotActionEnum.ATTACK):
            if bot.target == bot.player_id:
                bot.target = -1
            if models.Player.objects.filter(team = bot.team, player_id = bot.player_id).first():
                bot.target = -1
            if (closest_enemy and distance_to_enemy < 120 or override_target) and not bot.in_vehicle: # TODO: change this to x within viewing angle of y 
                # print(bot.in_vehicle)
                # print("attack enemy")
                # print('test')
                enemy_grid_pos =  current_level.transform.transform_to_grid((float(closest_enemy.transform['trans']['x']) , float(closest_enemy.transform['trans']['z'])))
                if override_target and models.Player.objects.filter(player_id=override_target_id).first():
                    if not models.Player.objects.filter(player_id=override_target_id).first().alive or models.Player.objects.filter(player_id=override_target_id).first().team == bot.team:
                        override_target = False
                        bot.overidden_target = -2
                

                # Not a great method, as this opens up the change that the bot will target a friendly.
                if not override_target:
                    bot.target = closest_enemy.player_id
                else:
                    bot.target = override_target_id

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
                if bot.in_vehicle and distance_to_objective < 5:
                    print('we can get out')
                    bot.order = orders.BotOrdersEnum.FRIENDLY
                    bot.action = orders.BotActionEnum.GET_OUT
                bot.save()

        elif bot.action == 6 and not bot.in_vehicle:
            # print("GETIN")
            target = models.Player.objects.filter(player_id=bot.target).first() or models.Bot.objects.filter(player_id=bot.target).first()
            if target:
                # print('valid path to get in vehicle')
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
            else:
                bot.action = orders.BotActionEnum.ATTACK
                bot.order = orders.BotOrdersEnum.ENEMY
            bot.save()

        # elif bot.in_vehicle == False and bot.action == 6:
        #     bot.action = 7
        
        elif bot.in_vehicle and (bot.order == 3 or bot.order == 4 or bot.action == 6):
            bot.order = 2
            bot.action = 2
            bot.target = -1
            bot.save()

        elif bot.action == 7:
            if not bot.in_vehicle:
                bot.action = orders.BotActionEnum.ATTACK
            bot.target = -1
            bot.save()
    else:
        bot.target = -1
        bot.order = 2
        bot.action = 2
        bot.path = []
        bot.save()

def get_nearest_vehicle(bot : models.Bot):
    nearest_vehicle = None
    nearest_vehicle_distance = math.inf
    for vehicle in navigation_models.Vehicle.objects.all():
        vehicle : navigation_models.Vehicle = vehicle
        d = distance(
            bot.transform['trans']['x'], bot.transform['trans']['y'], bot.transform['trans']['z'],
            vehicle.transform['trans']['x'], vehicle.transform['trans']['y'], vehicle.transform['trans']['z']
        )
        if d < nearest_vehicle_distance and len(vehicle.passengers) == 0:
            nearest_vehicle_distance = d
            nearest_vehicle = vehicle

    return nearest_vehicle, nearest_vehicle_distance

def compute_model(bot : models.Bot, current_level : Level, override_target = False, overidden_target = -2):
    if bot.alive and 'trans' in list(bot.transform.keys()):
        objectives : List[navigation_models.Objective] = get_target_objectives(bot.team, navigation_models.Objective)
        closest_objective, distance_to_objective = get_nearest_objective(bot, objectives)
        any_objectives = navigation_models.Objective.objects.count() > 0

        enemies : List[models.BasePlayer] = list(models.Bot.objects.exclude(team=bot.team).all()) + list(models.Player.objects.exclude(team=bot.team).all())
        current_level_model : navigation_models.Level = navigation_models.Level.objects.filter(level_id = current_level.model.level_id, project_id = current_level.model.project_id).first()
        closest_enemy, distance_to_enemy = get_nearest_enemy(bot, enemies)
        bot_grid_pos = current_level.transform.transform_to_grid((bot.transform['trans']['x'], bot.transform['trans']['z']))
        d = random.randrange(-2.0, 2.0)
        bot_forward_grid_pos = current_level.transform.transform_to_grid(
            (
                bot.transform['trans']['x'] + (bot.transform['forward']['x']*d),
                bot.transform['trans']['z'] + (bot.transform['forward']['z']*d)
            )
        )
        if False: #bot.stuck:
            back = [bot.transform['forward']['x']*-5, bot.transform['forward']['y']*-5, bot.transform['forward']['z']*-5]
            target = bot.transform['trans']['x'] + back[0], bot.transform['trans']['y'] + back[1], bot.transform['trans']['z'] + back[2]
            target_grid_pos = current_level.transform.transform_to_grid((target[0], target[2]))
            if False:#current_level.dffinder:
                valid_pos =  current_level.dffinder.ensure_point_valid((bot_grid_pos[0], bot_grid_pos[1], current_level.get_best_navmesh_level(
                    (target_grid_pos[0], target_grid_pos[1], bot.transform['trans']['y'])
                )))
                best_level = current_level.get_best_navmesh_level(
                    (bot_grid_pos[0], bot_grid_pos[1], bot.transform['trans']['y']))

                elevation = current_level.elevation[best_level][bot_grid_pos[0]][bot_grid_pos[1]]
                target_elevation = current_level.elevation[valid_pos[2]][valid_pos[0]][valid_pos[1]]
                path = [
                    (*current_level.transform.transform_to_world(bot_grid_pos), float(elevation)),
                    #(*current_level.transform.transform_to_world(valid_pos), float(target_elevation))
                ]
                bot.path = []
                for p in path:
                    bot.path.append(
                        {
                            'x': p[0],
                            'y': p[2],
                            'z': p[1]
                        }
                    )
                # bot.stuck = False
            else:
                bot.path = current_level.astar(
                    bot_grid_pos, target_grid_pos, elevation=bot.transform['trans']['y'], target_elevation = bot.transform['trans']['y']
                )
            if models.Player.objects.filter(team = bot.team, player_id = bot.player_id).first():
                bot.target = -1
            bot.order = 2
            bot.action = 2

        
        elif bot.action == int(orders.BotActionEnum.PROVIDE_AMMO) or bot.action == int(orders.BotActionEnum.PROVIDE_HEALTH):
            player_provider : models.Player = models.Player.objects.filter(player_id = bot.target).first()
            if player_provider:
                player_grid_pos = current_level.transform.transform_to_grid((player_provider.transform['trans']['x'], player_provider.transform['trans']['z']))
                if distance(
                    bot.transform['trans']['x'], bot.transform['trans']['y'], bot.transform['trans']['z'],
                    player_provider.transform['trans']['x'], player_provider.transform['trans']['y'], player_provider.transform['trans']['z']
                ) < 2.5:
                    bot.order = 2
                    bot.action = 2
                    bot.target = -1
                    bot.path = []
                    pass
                else:
                    bot.path = current_level.astar(
                        bot_grid_pos,
                        player_grid_pos,
                        elevation = bot.transform['trans']['y'],
                        target_elevation = player_provider.transform['trans']['y'],
                    )

        elif bot.action == int(orders.BotActionEnum.ATTACK):
            if (closest_enemy and distance_to_enemy < 30) and not bot.in_vehicle: # TODO: change this to x within viewing angle of y 
                # enemy_grid_pos =  current_level.transform.transform_to_grid((float(closest_enemy.transform['trans']['x']) , float(closest_enemy.transform['trans']['z'])))
                if override_target and models.Player.objects.filter(player_id=overidden_target).first():
                    if not models.Player.objects.filter(player_id=overidden_target).first().alive:
                        override_target = False
                        bot.overidden_target = -2

                # Not a great method, as this opens up the change that the bot will target a friendly.
                if not override_target:
                    bot.target = closest_enemy.player_id
                else:
                    bot.target = override_target
                if bot.player_id == bot.target:
                    bot.target = -1
                    return
                if bot.team == models.Player.objects.filter(player_id = bot.target).first().team:
                    bot.target = -1
                    return
                bot.order = orders.BotOrdersEnum.ENEMY
                # bot.action = orders.BotActionEnum.ATTACK

                # In-case it's overidden
                closest_enemy = models.Player.objects.filter(player_id = bot.target).first()
                if not closest_enemy:
                    bot.order = 2
                    bot.action = 2
                    bot.target = -1
                    return
                if not closest_enemy.alive:
                    bot.order = 2
                    bot.action = 2
                    bot.target = -1
                    return
                    
                enemy_grid_pos =  current_level.transform.transform_to_grid((float(closest_enemy.transform['trans']['x']) , float(closest_enemy.transform['trans']['z'])))

                bot_best_level = current_level.get_best_navmesh_level(
                    (*bot_grid_pos, bot.transform['trans']['y'])
                )
                enemy_best_level = current_level.get_best_navmesh_level(
                    (*enemy_grid_pos, closest_enemy.transform['trans']['y'])
                )

                # print("Total cost to enemy: ", 
                cost = current_level.get_cost_to(
                    (*bot_grid_pos, bot_best_level),
                    (*enemy_grid_pos, enemy_best_level)
                )
                print("Cost: ", cost)
                if cost > current_level_model.distance_field_threshold*0.8:
                    bot.target = -1
                    print(f"Cost is {cost}, not attacking until at path")

                bot.path = current_level.astar(
                    bot_forward_grid_pos,
                    enemy_grid_pos,
                    elevation=bot.transform['trans']['y'],
                    target_elevation = closest_enemy.transform['trans']['y']
                )
                #print("path")
                if type(bot.path ) == type(None):
                    bot.path = []
                else:
                    if len(bot.path) == 0:
                        bot.path = []
                # bot.save()

            elif closest_objective and any_objectives:
                print('no enemy, but close objective', closest_objective.name, closest_objective.team, closest_objective.controlled, bot.team)
                bot.path = []
                
                bot.target = -1
                bot.order = orders.BotOrdersEnum.OBJECTIVE

                end =  current_level.transform.transform_to_grid((float(closest_objective.transform['trans']['x']) , float(closest_objective.transform['trans']['z'])))
                print(distance_to_objective)
                if distance_to_objective > 50 and not bot.in_vehicle:
                    bot.order = orders.BotOrdersEnum.FRIENDLY
                    bot.action = orders.BotActionEnum.VEHICLE_DISCOVERY

                print("Finding from:", bot_grid_pos, "to:", end)
                path = current_level.astar(
                    bot_grid_pos,
                    end,
                    elevation=bot.transform['trans']['y'],
                    target_elevation = closest_objective.transform['trans']['y']
                )
                bot.path = path
                # print("path: ", bot.path)
                if bot.in_vehicle and distance_to_objective < 5:
                    # print('we can get out')
                    bot.order = orders.BotOrdersEnum.FRIENDLY
                    bot.action = orders.BotActionEnum.GET_OUT
                # bot.save()
            elif not any_objectives:
                targets : list = current_level_model.spawn_points_friendly
                target = targets[random.randint(0, len(targets)-1)]
                target_grid_pos = current_level.transform.transform_to_grid(
                    (
                        target['x'], target['z']
                    )
                )
                print("Random point", bot_grid_pos, target_grid_pos, target)
                bot.path = current_level.astar(
                    bot_grid_pos, 
                    target_grid_pos,
                    elevation = bot.transform['trans']['y'],
                    target_elevation = target['y']
                )

            elif bot.action == 6 and not bot.in_vehicle:
                target = models.Player.objects.filter(player_id=bot.target).first() or models.Bot.objects.filter(player_id=bot.target).first()
                if target:
                    # print('valid path to get in vehicle')
                    end =  current_level.transform.transform_to_grid((float(target.transform['trans']['x']) , float(target.transform['trans']['z'])))
                    bot.path = current_level.astar(
                            bot_forward_grid_pos,
                            end,
                            elevation=bot.transform['trans']['y'],
                            target_elevation = target.transform['trans']['y']
                        )
                    if type(bot.path ) == type(None):
                            bot.path = []
                    else:
                        if len(bot.path) == 0:
                            bot.path = []
                else:
                    bot.action = orders.BotActionEnum.ATTACK
                    bot.order = orders.BotOrdersEnum.ENEMY
                # bot.save()

        elif bot.action == orders.BotActionEnum.VEHICLE_DISCOVERY:
            if bot.in_vehicle:
                bot.action = 2
                bot.order = 2
                return
            nearest_vehicle, nearest_vehicle_distance = get_nearest_vehicle(bot)
            if nearest_vehicle:
                print("Vehicle Discovery", nearest_vehicle_distance)
                end = current_level.transform.transform_to_grid((float(nearest_vehicle.transform['trans']['x']), float(nearest_vehicle.transform['trans']['z'])))
                bot.path = current_level.astar(
                    bot_grid_pos,
                    end,
                    elevation= bot.transform['trans']['y'],
                    target_elevation= nearest_vehicle.transform['trans']['y']
                )
                bot.target_vehicle = nearest_vehicle.instance