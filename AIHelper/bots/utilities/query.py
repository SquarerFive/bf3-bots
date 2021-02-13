from bots import models

from typing import List, Tuple, Union

bot_step = 0

from . behaviour import distance
import datetime

def create_or_update_bot(bot : dict):
    b : models.Bot = models.Bot.objects.filter(player_id = bot['player_id']).first()
    if not b:
        name = f"ImABot{bot['bot_index']}"
        b = models.Bot.objects.create(
            player_id=bot['player_id'], 
            name=name, 
            team=bot['team'], 
            #action=bot['action'], 
            order = bot['order'], 
            health = bot['health'], 
            in_vehicle=bot['in_vehicle'], 
            transform=bot['transform'], 
            bot_index=bot['bot_index'],
            alive=bot['alive'],
            selected_kit = bot['kit'],
            last_transform_update = datetime.datetime.now(),
            last_transform = {},
            stuck=False
            )
    else:
        b.transform = bot['transform']
        b.health = bot['health']
        b.in_vehicle = bot['in_vehicle']
        b.team = bot['team']
        if int(bot['requested_order']) != b.order and int(bot['requested_order']) != -1:
            b.order = bot['order']
        if int(bot['requested_action']) != b.action and int(bot['requested_action']) != -1:
            b.action = bot['action']
        # print("reqa", bot['requested_action'])
        b.bot_index = bot['bot_index']
        b.alive = bot['alive']
        b.squad = bot['squad']
        #if int(bot['requested_target_id']) != -2:
        #    b.target = int(bot['requested_target_id'])
        b.overidden_target = int(bot['requested_target_id'])
        # b.save()

def create_or_update_bot_model(b : models.Bot, bot: dict):
    # b : models.Bot = models.Bot.objects.filter(player_id = bot['player_id']).first()
    if not b:
        name = f"ImABot{bot['bot_index']}"
        b = models.Bot.objects.create(
            player_id=bot['player_id'], 
            name=name, 
            team=bot['team'], 
            #action=bot['action'], 
            order = bot['order'], 
            health = bot['health'], 
            in_vehicle=bot['in_vehicle'], 
            transform=bot['transform'], 
            bot_index=bot['bot_index'],
            alive=bot['alive'],
            selected_kit = bot['kit'])
    else:
        b.transform = bot['transform']
        b.health = bot['health']
        b.in_vehicle = bot['in_vehicle']
        b.team = bot['team']
        if int(bot['requested_order']) != b.order and int(bot['requested_order']) != -1:
            b.order = bot['order']
        if int(bot['requested_action']) != b.action and int(bot['requested_action']) != -1:
            b.action = bot['action']
        # print("reqa", bot['requested_action'])
        b.bot_index = bot['bot_index']
        b.alive = bot['alive']
        b.squad = bot['squad']
        #if int(bot['requested_target_id']) != -2:
        #    b.target = int(bot['requested_target_id'])
        b.overidden_target = int(bot['requested_target_id'])

        delta = datetime.datetime.now().replace(tzinfo=b.last_transform_update.tzinfo) - b.last_transform_update
        if delta.total_seconds() > 8:
            b.last_transform_update = datetime.datetime.now()
            if 'trans' in list(b.last_transform.keys()):
                if distance(bot['transform']['trans']['x'], 0, bot['transform']['trans']['z'], 
                    b.last_transform['trans']['x'], 0, b.last_transform['trans']['z']) < 0.8:
                    b.stuck = True
                else:
                    b.stuck = False
            b.last_transform = bot['transform']
        # b.save()

def create_or_update_player(player : dict):
    # print("For player", player)
    p = models.Player.objects.filter(player_id=player['player_id']).first()
    if not p:
        p = models.Player.objects.create(
            player_id=player['player_id'],
            name=player['name'],
            online_id=player['online_id'],
            alive=player['alive'],
            is_squad_leader=player['is_squad_leader'],
            is_squad_private=player['is_squad_private'],
            in_vehicle=player['in_vehicle'],
            has_soldier=player['has_soldier'],
            team=player['team'],
            squad=player['squad'],
            health=player['health']
        )
        p.transform = player['transform']
        p.save()
    else:
        p.transform = player['transform']
        p.player_id = player['player_id']
        p.name = player['name']
        p.online_id = player['online_id']
        p.alive = player['alive']
        p.is_squad_leader = player['is_squad_leader']
        p.is_squad_private = player['is_squad_private']
        p.in_vehicle = player['in_vehicle']
        p.has_soldier = player['has_soldier']
        p.team = player['team']
        p.squad = player['squad']
        p.health = player['health']
        
        p.save()

def create_or_update_player_model(p : models.Player, player : dict):
    # print("For player", player)
    # p = models.Player.objects.filter(player_id=player['player_id']).first()
    if not p:
        p = models.Player.objects.create(
            player_id=player['player_id'],
            name=player['name'],
            online_id=player['online_id'],
            alive=player['alive'],
            is_squad_leader=player['is_squad_leader'],
            is_squad_private=player['is_squad_private'],
            in_vehicle=player['in_vehicle'],
            has_soldier=player['has_soldier'],
            team=player['team'],
            squad=player['squad'],
            health=player['health']
        )
        p.transform = player['transform']
        p.save()
    else:
        p.transform = player['transform']
        p.player_id = player['player_id']
        p.name = player['name']
        p.online_id = player['online_id']
        p.alive = player['alive']
        p.is_squad_leader = player['is_squad_leader']
        p.is_squad_private = player['is_squad_private']
        p.in_vehicle = player['in_vehicle']
        p.has_soldier = player['has_soldier']
        p.team = player['team']
        p.squad = player['squad']
        p.health = player['health']
        
        # p.save()

def get_bots_as_dict():
    global bot_step
    bots = models.Bot.objects.all()
    data = []
    all_data = []
    groups = 12
    for i in range(0, groups):
        data.append( [])
    # print(data)
    group_index = 0
    for bot in bots:
        #  d = bot.__dict__

        d = {
            "health": bot.health,
            "action": bot.action,
            "order": bot.order,
            "team": bot.team,
            "name": bot.name,
            "path": bot.path,
            "player_id": bot.player_id,
            "bot_index": bot.bot_index,
            "target": bot.target,
            "selected_kit": bot.selected_kit
        }
        all_data.append(d)
        # print(group_index)
        data[group_index].append(d)
        
        if group_index+1 < groups:
            group_index += 1
        else:
            group_index = 0
    current_step : int = bot_step
    bot_step += 1
    if bot_step > groups-1:
        bot_step = 0

    return all_data

def emit_and_propagate_action(instigator : int, order : int, action : int) -> bool:
    instigator : models.BasePlayer = models.Player.objects.filter(player_id=instigator).first() or models.Bot.objects.filter(player_id=instigator).first()
    print(instigator)
    friends : List[models.Bot] = list(models.Bot.objects.filter(squad=instigator.squad, team=instigator.team))
    print("friends", friends, 'action', action)
    for friend in friends:
        friend.order = order
        friend.action = action
        friend.target = instigator.player_id
        friend.save()
        
    
    return True