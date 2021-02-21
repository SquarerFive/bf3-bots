from django.http.response import HttpResponsePermanentRedirect
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.views import get_view_description

from . import serializers

import json

from .utils import query
from navigation.utilities import query as navigation_query
from navigation.utilities import level
from navigation import models as navigation_models

from bots.utilities import query as bots_query, behaviour
from bots import models as bots_models

import numpy as np
import pickle
import base64

from PIL import Image
from django.http import HttpResponse

from typing import List, Union

from manager import models

import random

from django.db import connection
import time

import pytz

from django.db.backends.signals import connection_created
from django.dispatch import receiver

from tqdm import tqdm

# @receiver(connection_created)
# def connection_init(sender, connection, **kwargv):
#     connection.cursor().execute("SET autocommit=1")

# Globals [to avoid poo memory, cache it here until the level changes]
class GlobalCache:
    def __init__(self):
        self.level_model : Union[level.models.Level, None] = None
        self.level_object : Union[level.Level, None] = None
        self.tasks = []

    def get_object(self, project_id : int, level_id : int):
        if self.level_object:
            if self.level_object.model.project_id == project_id and self.level_model.level_id == level_id:
                return self.level_object
        self.level_model = level.models.Level.objects.filter(project_id= project_id, level_id=level_id).first()
        self.level_object = navigation_query.decode_level(self.level_model)
        game_manager = models.BF3GameManager.objects.first()
        if game_manager == None:
            game_manager = models.BF3GameManager(active_project_id = project_id, active_level_id=level_id)
            game_manager.save()
        else:
            game_manager.active_project_id = project_id
            game_manager.active_level_id = level_id
            game_manager.save()
        print('load level', project_id, level_id)
        return self.level_object

    def save_object(self):
        if self.level_object:
            navigation_query.encode_level(self.level_object)

global_cache = GlobalCache()

# Create your views here.

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def manager_base(request: Request, format=None) -> Response:
    return Response("Successfully got response!")


@api_view(['POST'])
@permission_classes([AllowAny])
def manager_login(request: Request, format=None) -> Response:
    data = json.loads(request.body.decode('utf-8'))
    print("logging in")
    success, token = query.login_user(data['username'], data['password'])
    # print(success, token)
    if success:
        data = {
            'username': data['username'],
            'token': token
        }
        return Response(data)
    else:
        return Response("Invalid credentials", status=401)


@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_create_project(request: Request, format=None) -> Response:
    print("Create project")
    data = json.loads(request.body.decode('utf-8'))
    query.create_project(
        name=data['name'], author_username=request.user.username, description=data['description'])
    return Response("Created project")


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_projects(request: Request, format=None) -> Response:
    data = {
        'projects': [json.loads(JSONRenderer().render(serializers.ProjectSerializer(j).data)) for j in query.navigation_models.Project.objects.all()]
    }
    return Response(data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_project(request: Request, project_id: int, format=None) -> Response:
    return Response(
        json.loads(JSONRenderer().render(serializers.ProjectSerializer(
            query.navigation_models.Project.objects.filter(
                project_id=project_id).first()
        ).data)), content_type='application/json'
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_levels(request: Request, project_id: int, format=None) -> Response:
    data = {
        'levels': [json.loads(JSONRenderer().render(
            serializers.LevelSerializer(j).data
        )) for j in query.navigation_models.Level.objects.filter(project_id=project_id)]
    }
    for idx, level in enumerate(data['levels']):
        if data['levels'][idx]['friendly_kit']:
            data['levels'][idx]['friendly_kit'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitCollectionSerializer(models.SoldierKitCollection.objects.filter(id=data['levels'][idx]['friendly_kit'], faction=0).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['friendly_kit']['assault'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['friendly_kit']['id'], collection_slot=0).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['friendly_kit']['engineer'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['friendly_kit']['id'], collection_slot=1).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['friendly_kit']['support'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['friendly_kit']['id'], collection_slot=2).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['friendly_kit']['recon'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['friendly_kit']['id'], collection_slot=3).first()).data
            ).decode('utf-8'))
        if data['levels'][idx]['enemy_kit']:
            data['levels'][idx]['enemy_kit'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitCollectionSerializer(models.SoldierKitCollection.objects.filter(id=data['levels'][idx]['enemy_kit'], faction=1).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['enemy_kit']['assault'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['enemy_kit']['id'], collection_slot=0).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['enemy_kit']['engineer'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['enemy_kit']['id'], collection_slot=1).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['enemy_kit']['support'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['enemy_kit']['id'], collection_slot=2).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['enemy_kit']['recon'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['enemy_kit']['id'], collection_slot=3).first()).data
            ).decode('utf-8'))
    return Response(data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_level(request: Request, project_id: int, level_id: int):
    level_dict = json.loads(JSONRenderer().render(serializers.LevelSerializer(
            query.navigation_models.Level.objects.filter(
                project_id=project_id, level_id=level_id).first()).data))
    if level_dict['friendly_kit']:
        level_dict['friendly_kit'] = json.loads(JSONRenderer().render(
            serializers.SoldierKitCollectionSerializer(models.SoldierKitCollection.objects.filter(id=level_dict['friendly_kit'], faction=0).first()).data
        ).decode('utf-8'))
        level_dict['friendly_kit']['assault'] = json.loads(JSONRenderer().render(
            serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=level_dict['friendly_kit']['id'], collection_slot=0).first()).data
        ).decode('utf-8'))
        level_dict['friendly_kit']['engineer'] = json.loads(JSONRenderer().render(
            serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=level_dict['friendly_kit']['id'], collection_slot=1).first()).data
        ).decode('utf-8'))
        level_dict['friendly_kit']['support'] = json.loads(JSONRenderer().render(
            serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=level_dict['friendly_kit']['id'], collection_slot=2).first()).data
        ).decode('utf-8'))
        level_dict['friendly_kit']['recon'] = json.loads(JSONRenderer().render(
            serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=level_dict['friendly_kit']['id'], collection_slot=3).first()).data
        ).decode('utf-8'))
    if level_dict['enemy_kit']:
        level_dict['enemy_kit'] = json.loads(JSONRenderer().render(
            serializers.SoldierKitCollectionSerializer(models.SoldierKitCollection.objects.filter(id=level_dict['enemy_kit'], faction=1).first()).data
        ).decode('utf-8'))
        level_dict['enemy_kit']['assault'] = json.loads(JSONRenderer().render(
            serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=level_dict['enemy_kit']['id'], collection_slot=0).first()).data
        ).decode('utf-8'))
        level_dict['enemy_kit']['engineer'] = json.loads(JSONRenderer().render(
            serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=level_dict['enemy_kit']['id'], collection_slot=1).first()).data
        ).decode('utf-8'))
        level_dict['enemy_kit']['support'] = json.loads(JSONRenderer().render(
            serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=level_dict['enemy_kit']['id'], collection_slot=2).first()).data
        ).decode('utf-8'))
        level_dict['enemy_kit']['recon'] = json.loads(JSONRenderer().render(
            serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=level_dict['enemy_kit']['id'], collection_slot=3).first()).data
        ).decode('utf-8'))
    return Response(level_dict)


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([AllowAny])
def manager_render_level(request: Request, project_id: int, level_id: int, raster_type: int, raster_layer: int):
    global global_cache
    level_object = global_cache.get_object(project_id, level_id)
    # level = query.navigation_models.Level.objects.filter(project_id=project_id, level_id=level_id).first()
    if level_object:
        print('rendering level')
        # level_object = navigation_query.decode_level(level)
        # level_object.classify_costs()
        # global_cache.save_object()
        # level_object.astar((403, 609), (560, 705))
        cost_surface = level_object.costs[raster_layer]
        print(cost_surface.shape)
        image = Image.fromarray(((cost_surface*255) / np.nanmax(cost_surface[cost_surface != np.inf])).astype(np.uint8), mode="L")
        response = HttpResponse(content_type='image/png')
        image.save(response, "PNG")
        return response
    return Response("Failed to render")

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_add_level(request : Request, project_id : int):
    data = json.loads(request.body.decode('utf-8'))
    level_name = str(request.headers['Level'])
    # min_point = str(request.headers['Min'])
    # max_point = str(request.headers['Max'])
    new_level = level.Level(level_name,  ((float(request.headers['Min-X'].replace("'", "")), float(request.headers['Min-Y'].replace("'", ""))),
            (float(request.headers['Max-X'].replace("'", "") ), float(request.headers['Max-Y'].replace("'", ""))),
            int(float(str(request.headers['Size-X']).replace("'", ""))),
            int(float(str(request.headers['Size-Y']).replace("'","") ))), data)
    new_level.project_id = project_id
    new_level.pre_process_data()
    # new_level.post_process_data()
    navigation_query.encode_level(new_level)
    return Response("Success")

class LevelBlockInterface:
    # x: int
    # y: int
    # elevation: float
    # values: List[float]

    def __init__(self, data : dict):
        self.x : int = int(data['x'])
        self.y : int = int(data['y']) 
        self.elevation : float = float(data['elevation'])
        self.values : List[float] = data['values']

def push_level_block(slot : LevelBlockInterface, levelObject : level.Level):
    # print(slot.values)
    df_sum = 0.0
    try:
        for level, value in enumerate(slot.values):
            levelObject.set_elevation_at(value['elevation'], slot.x, slot.y, level)
            levelObject.set_data_at(value['value'], slot.x, slot.y, level)
            levelObject.set_df_at(value['df'], slot.x, slot.y, level)
            df_sum += value['df']
    except Exception as e:
        print(slot.values, e)
        # levelObject.set_elevation_at(slot.values[0][0]['elevation'], slot.x, slot.y)
        # levelObject.set_data_at(slot.values[0][0]['value'], slot.x, slot.y)
    return df_sum

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_add_level_block(request : Request, project_id : int):
    data : List[LevelBlockInterface] = json.loads(request.body.decode('utf-8'))
    # list of { x: Int, y: Int, elevation: Float, values: Float[] }
    level_name = str(request.headers['Level'])
    levelModel = navigation_query.models.Level.objects.filter(project_id=project_id, name=level_name).first()

    #levelObject = navigation_query.decode_level(levelModel)
    if not levelModel:
        print('creating object')
        levelObject = level.Level(level_name, ((float(request.headers['Min-X'].replace("'", "")), float(request.headers['Min-Y'].replace("'", ""))),
            (float(request.headers['Max-X'].replace("'", "") ), float(request.headers['Max-Y'].replace("'", ""))),
            int(float(str(request.headers['Size-X']).replace("'", ""))),
            int(float(str(request.headers['Size-Y']).replace("'","") ))), None)
        use_df = str(request.headers['Has-DF']).lower().strip() == 'true'
        layers = int(request.headers['Layers'])
        global_cache.level_model.layers = layers
        global_cache.level_model.has_distance_field = use_df
        levelObject.project_id = project_id
        levelObject.pre_process_data(layers)
        navigation_query.encode_level(levelObject)
        levelModel = navigation_query.models.Level.objects.filter(project_id=project_id, name=level_name).first()
    



    levelModel = navigation_query.models.Level.objects.filter(project_id=project_id, name=level_name).first()
    # d = models.ProjectTaskJSON.objects.create(
    #     level_id=levelModel.level_id,
    #     project_id=project_id,
    #     name='NavGridBuildTask',
    #     task_id=models.ProjectTaskJSON.objects.count()+1
    # )
    # d.data = data
    # d.save()
    global_cache.tasks.append({
        'level_id': levelModel.level_id,
        'project_id': project_id,
        'name': 'NavGridBuildTask',
        'task_id': random.randint(0, 989898),
        'data': data
    })
    
    # if levelObject and levelModel:
    #     for slot in data:
    #        push_level_block(LevelBlockInterface(slot), levelObject)
    #     levelObject.classify_costs()
    #     navigation_query.encode_level(levelObject)
    # else:
    #     levelObject = level.Level(level_name, ((float(request.headers['Min-X'].replace("'", "")), float(request.headers['Min-Y'].replace("'", ""))),
    #         (float(request.headers['Max-X'].replace("'", "") ), float(request.headers['Max-Y'].replace("'", ""))),
    #         int(float(str(request.headers['Size-X']).replace("'", ""))),
    #         int(float(str(request.headers['Size-Y']).replace("'","") ))), None)
    #     levelObject.pre_process_data()
    #     for slot in data:
    #         push_level_block(LevelBlockInterface(slot), levelObject)
    #     # levelObject.classify_costs()
    #     navigation_query.encode_level(levelObject)
    return Response('Success!')

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_complete_level_block(request: Request, project_id : int) -> Response:
    global global_cache
    level_name = str(request.headers['Level'])
    # all we need to do is complete the rasterization
    levelModel = navigation_query.models.Level.objects.filter(project_id=project_id, name=level_name).first()
    levelObject = global_cache.get_object(project_id, levelModel.level_id)
    # levelObject = navigation_query.decode_level(levelModel)
    for task in models.ProjectTaskJSON.objects.all():
        # levelModel = navigation_query.models.Level.objects.filter(project_id=task.project_id, level_id=task.level_id).first()
        # levelObject = navigation_query.decode_level(levelModel)
        for slot in task.data:
            push_level_block(LevelBlockInterface(slot), levelObject)

    if levelObject:
        levelObject.classify_costs()
        global_cache.save_object()
        # navigation_query.encode_level(levelObject)
    else:
        return Response('Failed to find level', status=404)
    return Response('Success!')

# Clear level, and use new boundaries
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_clear_level_data(request : Request, project_id : int) -> Response:
    global global_cache
    level_name = str(request.headers['Level'])
    levelModel = navigation_query.models.Level.objects.filter(project_id=project_id, name=level_name).first()
    levelObject = global_cache.get_object(project_id, levelModel.level_id)
    # levelObject = navigation_query.decode_level(levelModel)
    transform = ((float(request.headers['Min-X'].replace("'", "")), float(request.headers['Min-Y'].replace("'", ""))),
            (float(request.headers['Max-X'].replace("'", "") ), float(request.headers['Max-Y'].replace("'", ""))),
            int(float(str(request.headers['Size-X']).replace("'", ""))),
            int(float(str(request.headers['Size-Y']).replace("'","") )))
    transformObj = level.transformations.GridTransform(transform[0], transform[1], transform[2], transform[3])
    use_df = str(request.headers['Has-DF']).lower().strip() == 'true'
    layers = int(request.headers['Layers'])
    print('clearing level', 'has levels:', layers)
    if levelObject:
        levelObject.transform = transformObj
        global_cache.level_model.layers = layers
        global_cache.level_model.has_distance_field = use_df
        global_cache.level_model.save()
        levelObject.pre_process_data(layers)
        # navigation_query.encode_level(levelObject)
        global_cache.save_object()
    else:
        print('failed to find level :(')
        return Response('Failed to find level.', status=404)
    return Response('Success!')

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def manager_reset_level_data(request : Request, project_id : int, level_id : int) -> Response:
    global global_cache
    level_object = global_cache.get_object(project_id, level_id)
    if level_object:
        level_object.pre_process_data()
        global_cache.save_object()
        for objective in navigation_models.Objective.objects.all():
            objective.delete()
        return Response("Level reset successful")
    else:
        pass
    return Response("Level not found.", status=404)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def manager_on_level_loaded(request : Request, project_id : int, level_id : int) -> Response:
    global global_cache
    level_object = global_cache.get_object(project_id, level_id)
    if level_object:
        for objective in navigation_models.Objective.objects.all():
            objective.delete()
        return Response("Old level cleared successfully")
    return Response("LEvel not found", status=404)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_level_id(request : Request, project_id : int) -> Response:
    data = request.data
    level = navigation_models.Level.objects.filter(project_id = project_id, name=data['level_name']).first()
    if level:
        return Response(level.level_id)
    else:
        return Response('error')

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_tasks(request : Request, project_id : int) -> Response:
    data = []
    i = 0
    for task in models.ProjectTaskJSON.objects.all():
        data.append(json.loads(
            JSONRenderer().render(serializers.ProjectTaskJSONSerializer(
                task
            ).data).decode('utf-8'))
        )
        i += 1
        if (i > 200):
            break
        # task.task_id = i
        # task.save()
    datadenc = json.dumps(data)
    dataenc = json.loads(datadenc)
    return Response(dataenc, content_type='application/json')

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_start_all_tasks(request: Request, project_id : int) -> Response:
    global global_cache
    print("starting tasks")
    first_task = models.ProjectTaskJSON.objects.first()
    bf3Model = models.BF3GameManager.objects.first()
    levelModel = navigation_query.models.Level.objects.filter(project_id=bf3Model.active_project_id, level_id=bf3Model.active_level_id).first()
    # levelObject = navigation_query.decode_level(levelModel)
    # t_models = []
    # for task in global_cache.tasks:
    #     d = models.ProjectTaskJSON.objects.create(
    #         level_id=task['level_id'],
    #         project_id=task['project_id'],
    #         name=task['name'],
    #         task_id=models.ProjectTaskJSON.objects.count()+1
    #     )
    #     d.data = task['data']
    #     t_models.append(d)
    # models.ProjectTaskJSON.objects.bulk_update(t_models, ['data',])

    levelObject = global_cache.get_object(project_id, levelModel.level_id)
    print("Level Object Info: ", levelObject.data.shape, levelObject.costs.shape, levelObject.elevation.shape)
    levelObject.sensecheck()
    global_cache.save_object()
    pbar = tqdm(global_cache.tasks)
    pbar.set_description('Running tasks')
    i = 0
    for task in pbar:
        if levelModel.level_id != task['level_id'] or levelModel.project_id != task['project_id']:
            levelObject.classify_costs()
            # navigation_query.encode_level(levelObject)
            global_cache.save_object()
            levelModel = navigation_query.models.Level.objects.filter(project_id=task['project_id'], level_id=task['level_id']).first()
            # levelObject = navigation_query.decode_level(levelModel)
            levelObject = global_cache.get_object(project_id, levelModel.level_id)
        j = 0
        # data_pbar = tqdm(task['data'])
        # data_pbar.set_description('Processing task data')
        df_sum = 0.0
        for slot in task['data']:
            df_sum += push_level_block(LevelBlockInterface(slot), levelObject)
            
            j+= 1
        pbar.set_description(f'Processing task data | DF Sum: {df_sum}')
        i += 1
    global_cache.tasks.clear()
    levelObject.classify_costs()
    # navigation_query.encode_level(levelObject)
    global_cache.save_object()
    print('done')
    models.ProjectTaskJSON.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute('vacuum;')
        
    return Response('Success')

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_add_level_feature(request: Request, project_id : int, level_id : int, feature_type: str):
    global global_cache
    global_cache.get_object(project_id, level_id)
    level_model = global_cache.level_model
    # level_model : navigation_models.Level = navigation_query.models.Level.objects.filter(project_id=project_id, level_id=level_id).first()
    if feature_type == 'road':
        level_model.roads = json.loads(request.body.decode('utf-8'))
        level_model.save()
        print(level_model.roads, type(level_model.roads))
    if feature_type == 'structure':
        level_model.structures = json.loads(request.body.decode('utf-8'))
        level_model.save()
        print("Added structure", level_model.structures)
    global_cache.save_object()
    return Response('Success')

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([AllowAny])
def manager_update_level(request: Request, project_id : int) -> Response:
    global global_cache
    
    data = json.loads(request.body.decode('utf-8'))
    level_name = str(request.headers['Level'])
    level_model : navigation_models.Level = level.models.Level.objects.filter(name=level_name, project_id=project_id).first()
    
    if level_model:
        level_object = global_cache.get_object(project_id, level_model.level_id)
        settings : models.BF3GameManager = models.BF3GameManager.objects.first()
        if settings.active_level_id != level_model.level_id or settings.active_project_id != level_model.project_id:
            settings.active_project_id = level_model.project_id
            settings.active_level_id = level_model.level_id
            settings.reload = True
            settings.save()
        
        friendly_faction_kit_collection : models.SoldierKitCollection = models.SoldierKitCollection.objects.filter(project_id=project_id, level_id=level_model.level_id, faction=0).first()
        enemy_faction_kit_collection : models.SoldierKitCollection = models.SoldierKitCollection.objects.filter(project_id=project_id, level_id=level_model.level_id, faction=1).first()
        players = bots_models.Player.objects.all()
        objectives = navigation_models.Objective.objects.all()
        
        for objective in data['objectives']:
            navigation_query.add_objective(objective)
        ts = time.time()
        p_array = []
        for player in data['players']:
            player_m = players.filter(player_id=player['player_id']).first()
            if player_m:
                bots_query.create_or_update_player_model(player_m, player)
                p_array.append(player_m)
            else:
                bots_query.create_or_update_player(player)

        bots_models.Player.objects.bulk_update(p_array, ['transform', 'player_id', 'name', 'online_id', 'alive', 'is_squad_leader', 'is_squad_private', 'in_vehicle', 'has_soldier', 'team', 'squad', 'health',
            'health_provider', 'ammo_provider'])
        
        bots = bots_models.Bot.objects.all()
        b_array = []
        # print("doing bots, ", data['bots'])
        for bot in data['bots']:
            bot_model = bots.filter(bot_index=bot['bot_index']).first()
            
            if (bot_model):
                
                b_array.append(bot_model)
            
                active_collection = friendly_faction_kit_collection if bot['team'] == 0 else enemy_faction_kit_collection
                if active_collection:
                    kits = [
                        models.SoldierKit.objects.filter(collection_id=active_collection.id, collection_slot=0).first(),
                        models.SoldierKit.objects.filter(collection_id=active_collection.id, collection_slot=1).first(),
                        models.SoldierKit.objects.filter(collection_id=active_collection.id, collection_slot=2).first(),
                        models.SoldierKit.objects.filter(collection_id=active_collection.id, collection_slot=3).first(),
                    ]
                    kit = kits[random.randint(0,3)]
                    bot['kit'] = {
                        'primary_weapon': kit.primary_weapon[random.randint(0, len(kit.primary_weapon))-1] if len(kit.primary_weapon) > 0 else None,
                        'secondary_weapon': kit.secondary_weapon[random.randint(0, len(kit.secondary_weapon))-1] if len(kit.secondary_weapon) > 0 else None,
                        'primary_gadget': kit.primary_gadget[random.randint(0, len(kit.primary_gadget))-1] if len(kit.primary_gadget) > 0 else None,
                        'secondary_gadget': kit.secondary_gadget[random.randint(0, len(kit.secondary_gadget))-1] if len(kit.secondary_gadget) > 0 else None,
                        'melee': kit.melee[random.randint(0, len(kit.melee))-1] if len(kit.melee) > 0 else None,
                        'unlocks': kit.appearance[random.randint(0, len(kit.melee))-1] if len(kit.appearance) > 0 else None,
                        'kit_asset': kit.kit_asset
                    }
                    bot['ammo_provider'] = bot['kit']['primary_gadget']['name'] == 'U_Ammobag'
                    bot['health_provider'] = bot['kit']['primary_gadget']['name'] == 'U_Medkit'
                    # bots_query.create_or_update_bot(bot)
                bots_query.create_or_update_bot_model(bot_model, bot)
            else:
                active_collection = friendly_faction_kit_collection if bot['team'] == 0 else enemy_faction_kit_collection
                if active_collection:
                    kits = [
                        models.SoldierKit.objects.filter(collection_id=active_collection.id, collection_slot=0).first(),
                        models.SoldierKit.objects.filter(collection_id=active_collection.id, collection_slot=1).first(),
                        models.SoldierKit.objects.filter(collection_id=active_collection.id, collection_slot=2).first(),
                        models.SoldierKit.objects.filter(collection_id=active_collection.id, collection_slot=3).first(),
                    ]
                    kit = kits[random.randint(0,3)]
                    bot['kit'] = {
                        'primary_weapon': kit.primary_weapon[random.randint(0, len(kit.primary_weapon))-1] if len(kit.primary_weapon) > 0 else None,
                        'secondary_weapon': kit.secondary_weapon[random.randint(0, len(kit.secondary_weapon))-1] if len(kit.secondary_weapon) > 0 else None,
                        'primary_gadget': kit.primary_gadget[random.randint(0, len(kit.primary_gadget))-1] if len(kit.primary_gadget) > 0 else None,
                        'secondary_gadget': kit.secondary_gadget[random.randint(0, len(kit.secondary_gadget))-1] if len(kit.secondary_gadget) > 0 else None,
                        'melee': kit.melee[random.randint(0, len(kit.melee))-1] if len(kit.melee) > 0 else None,
                        'unlocks': kit.appearance[random.randint(0, len(kit.melee))-1] if len(kit.appearance) > 0 else None,
                        'kit_asset': kit.kit_asset
                    }
                    bot['ammo_provider'] = bot['kit']['primary_gadget']['name'] == 'U_Ammobag'
                    bot['health_provider'] = bot['kit']['primary_gadget']['name'] == 'U_Medkit'
                    bots_query.create_or_update_bot(bot)
            # behaviour.compute(bot['bot_index'], level_object, bots_models.Bot, bots_models.Player, navigation_models.Objective, int(bot['requested_target_id'])!=-2, int(bot['requested_target_id']))
        bots_models.Bot.objects.bulk_update(b_array, ['transform', 'health', 'in_vehicle', 'team', 'order', 'action', 'bot_index', 'alive', 'squad', 'overidden_target', 'last_transform', 'last_transform_update', 'stuck'])
        data = {
            "bots" : bots_query.get_bots_as_dict()
        }
        response_data = json.dumps(data)
        # print(response_data)
        te = time.time()
        print("Time to update level: ", te-ts)
        return HttpResponse(response_data)
    print('no level')
    return Response('Failed to find level {0} for current project {1}'.format(level_name, project_id), status=404)

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([AllowAny])
def manager_emit_event(request : Request) -> Response:
    print(request.data)
    print('emit event')
    data = request.data
    bots_query.emit_and_propagate_action(
        data['Instigator'],
        data['Order'],
        data['Action']
    )
    return Response('Success')

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_clear_tasks(request : Request) -> Response:
    models.ProjectTaskJSON.objects.all().delete()
        

    table_name = models.ProjectTaskJSON._meta.db_table
    with connection.cursor() as cursor:
        #cursor.execute(f"DROP TABLE {table_name};")
        cursor.execute('vacuum;')
    return Response("Done!")

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def manager_recalculate_costs(request : Request, project_id : int, level_id : int) -> Response:
    global global_cache
    level_object = global_cache.get_object(project_id, level_id)
    print(request.data)
    elevation_based = request.data['elevation_based_scoring']
    elevation_alpha_power = float(request.data['elevation_alpha_power'])
    elevation_alpha_beta = float(request.data['elevation_alpha_beta'])
    elevation_alpha_beta_power = float(request.data['elevation_alpha_beta_power'])
    use_df = bool(request.data['use_df'])
    if level_object:
        level_object.classify_costs(elevation_based, elevation_alpha_power, elevation_alpha_beta, elevation_alpha_beta_power, use_df=use_df)
        global_cache.save_object()
        print("Saving")
        return Response("Success!")
    return Response("Failed to find level!", status=404)

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_import_asset_from_csv(request : Request) -> Response:
    import csv
    filename = request.data['filename']
    with open(filename, newline='') as asset_import:
        asset_reader = csv.reader(asset_import, delimiter=',', quotechar='|')
        data = {}
        for index, row in enumerate(asset_reader):
            if index == 0:
                for col in row:
                    data[col] = []
                # print(data)
            else:
                for col_index, col in enumerate(row):
                    data[list(data.keys())[col_index]].append(col)
        # print(data)
    
        for index, name in enumerate(data['Name']):
            asset_name = name.split("/")[-1]
            asset_path = name
            is_us = int(data['US'][index])==1
            is_ru = int(data['RU'][index])==1
            asset_team = 'ALL'
            if is_us and is_ru:
                asset_team = 'BOTH'
            elif is_us:
                asset_team = 'US'
            else:
                asset_team = 'RU'
            tags = json.loads(data['Tags'][index])
            # print(is_us, is_ru)
            models.GameAsset.objects.create(name=asset_name, path=asset_path, asset_type=data['Category'][index], asset_team=asset_team, tags=tags)

    return Response("Success")

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_assets(request : Request) -> Response:
    assets = []
    for task in models.ProjectTaskJSON.objects.all():
        task.delete()
    for asset in models.GameAsset.objects.all():
        assets.append(
            json.loads(
                JSONRenderer().render(serializers.GameAssetSerializer(
                    asset
                ).data).decode('utf-8')
        ))
    return Response(assets)# content_type='application/json')

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_soldier_kits(request : Request, project_id : int, level_id : int) -> Response:
    level : navigation_models.Level = navigation_models.Level.objects.filter(level_id=level_id, project_id = project_id).first()
    # level.friendly_kit.
    return Response('inev')

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def manager_push_soldier_kit_data(request : Request, project_id : int, level_id : int) -> Response:
    global_cache.get_object(project_id, level_id)
    print(project_id, level_id)
    data = request.data
    
    # enemy_kit = models.SoldierKitCollection.objects.create()
    friendly_kit : models.SoldierKitCollection = models.SoldierKitCollection.objects.filter(level_id = level_id, project_id = project_id, faction = 0).first()
    if not friendly_kit:
        friendly_kit : models.SoldierKitCollection = models.SoldierKitCollection.objects.create()
    friendly_kit.faction = 0
    friendly_kit.project_id = project_id
    friendly_kit.level_id = level_id
    
    if not friendly_kit.assault:
        assault : models.SoldierKit = models.SoldierKit.objects.create()
        assault.primary_weapon = data['friendly']['assault']['primary_weapon']
        # assault.primary_attachments = data['friendly']['assault']['primary_attachments']
        assault.secondary_weapon = data['friendly']['assault']['secondary_weapon']
        # assault.secondary_attachments = data['friendly']['assault']['secondary_attachments']
        assault.primary_gadget = data['friendly']['assault']['primary_gadget']
        assault.secondary_gadget = data['friendly']['assault']['secondary_gadget']
        assault.melee = data['friendly']['assault']['melee']
        assault.collection_slot = 0
        assault.collection_id = friendly_kit.id
        assault.appearance = data['friendly']['assault']['appearance']
        assault.kit_asset = data['friendly']['assault']['kit_asset']
        assault.save()
        friendly_kit.assault = assault
    else:
        assault : models.SoldierKit = models.SoldierKit.objects.filter(collection_slot = 0, collection_id = friendly_kit.id).first()
        assault.primary_weapon = data['friendly']['assault']['primary_weapon']
        # assault.primary_attachments = data['friendly']['assault']['primary_attachments']
        assault.secondary_weapon = data['friendly']['assault']['secondary_weapon']
        # assault.secondary_attachments = data['friendly']['assault']['secondary_attachments']
        assault.primary_gadget = data['friendly']['assault']['primary_gadget']
        assault.secondary_gadget = data['friendly']['assault']['secondary_gadget']
        assault.melee = data['friendly']['assault']['melee']
        assault.collection_slot = 0
        assault.collection_id = friendly_kit.id
        assault.appearance = data['friendly']['assault']['appearance']
        assault.kit_asset = data['friendly']['assault']['kit_asset']
        assault.save()

    if not friendly_kit.engineer:
        engineer : models.SoldierKit = models.SoldierKit.objects.create()
        engineer.primary_weapon = data['friendly']['engineer']['primary_weapon']
        # engineer.primary_attachments = data['friendly']['engineer']['primary_attachments']
        engineer.secondary_weapon = data['friendly']['engineer']['secondary_weapon']
        # engineer.secondary_attachments = data['friendly']['engineer']['secondary_attachments']
        engineer.primary_gadget = data['friendly']['engineer']['primary_gadget']
        engineer.secondary_gadget = data['friendly']['engineer']['secondary_gadget']
        engineer.melee = data['friendly']['engineer']['melee']
        engineer.collection_slot = 1
        engineer.collection_id = friendly_kit.id
        engineer.appearance = data['friendly']['engineer']['appearance']
        engineer.kit_asset = data['friendly']['engineer']['kit_asset']
        engineer.save()
        friendly_kit.engineer = engineer
    else:
        engineer : models.SoldierKit = models.SoldierKit.objects.filter(collection_slot = 1, collection_id = friendly_kit.id).first()
        engineer.primary_weapon = data['friendly']['engineer']['primary_weapon']
        # engineer.primary_attachments = data['friendly']['engineer']['primary_attachments']
        engineer.secondary_weapon = data['friendly']['engineer']['secondary_weapon']
        # engineer.secondary_attachments = data['friendly']['engineer']['secondary_attachments']
        engineer.primary_gadget = data['friendly']['engineer']['primary_gadget']
        engineer.secondary_gadget = data['friendly']['engineer']['secondary_gadget']
        engineer.melee = data['friendly']['engineer']['melee']
        engineer.collection_slot = 1
        engineer.collection_id = friendly_kit.id
        engineer.appearance = data['friendly']['engineer']['appearance']
        engineer.kit_asset = data['friendly']['engineer']['kit_asset']
        engineer.save()

    if not friendly_kit.support:
        support : models.SoldierKit = models.SoldierKit.objects.create()
        support.primary_weapon = data['friendly']['support']['primary_weapon']
        # support.primary_attachments = data['friendly']['support']['primary_attachments']
        support.secondary_weapon = data['friendly']['support']['secondary_weapon']
        # support.secondary_attachments = data['friendly']['support']['secondary_attachments']
        support.primary_gadget = data['friendly']['support']['primary_gadget']
        support.secondary_gadget = data['friendly']['support']['secondary_gadget']
        support.melee = data['friendly']['support']['melee']
        support.collection_slot = 2
        support.collection_id = friendly_kit.id
        support.appearance = data['friendly']['support']['appearance']
        support.kit_asset = data['friendly']['support']['kit_asset']
        support.save()
        friendly_kit.support = support
    else:
        support : models.SoldierKit = models.SoldierKit.objects.filter(collection_slot = 2, collection_id = friendly_kit.id).first()
        support.primary_weapon = data['friendly']['support']['primary_weapon']
        # support.primary_attachments = data['friendly']['support']['primary_attachments']
        support.secondary_weapon = data['friendly']['support']['secondary_weapon']
        # support.secondary_attachments = data['friendly']['support']['secondary_attachments']
        support.primary_gadget = data['friendly']['support']['primary_gadget']
        support.secondary_gadget = data['friendly']['support']['secondary_gadget']
        support.melee = data['friendly']['support']['melee']
        support.collection_slot = 2
        support.collection_id = friendly_kit.id
        support.appearance = data['friendly']['support']['appearance']
        support.kit_asset = data['friendly']['support']['kit_asset']
        support.save()
    
    if not friendly_kit.recon:
        recon : models.SoldierKit = models.SoldierKit.objects.create()
        recon.primary_weapon = data['friendly']['recon']['primary_weapon']
        # recon.primary_attachments = data['friendly']['recon']['primary_attachments']
        recon.secondary_weapon = data['friendly']['recon']['secondary_weapon']
        # recon.secondary_attachments = data['friendly']['recon']['secondary_attachments']
        recon.primary_gadget = data['friendly']['recon']['primary_gadget']
        recon.secondary_gadget = data['friendly']['recon']['secondary_gadget']
        recon.melee = data['friendly']['recon']['melee']
        recon.collection_slot = 3
        recon.collection_id = friendly_kit.id
        recon.appearance = data['friendly']['recon']['appearance']
        recon.kit_asset = data['friendly']['recon']['kit_asset']
        recon.save()
        friendly_kit.recon = recon
    else:
        recon : models.SoldierKit = models.SoldierKit.objects.filter(collection_slot = 3, collection_id = friendly_kit.id).first()
        recon.primary_weapon = data['friendly']['recon']['primary_weapon']
        recon.secondary_weapon = data['friendly']['recon']['secondary_weapon']
        # recon.primary_attachments = data['friendly']['recon']['primary_attachments']
        # recon.secondary_attachments = data['friendly']['recon']['secondary_attachments']
        recon.primary_gadget = data['friendly']['recon']['primary_gadget']
        recon.secondary_gadget = data['friendly']['recon']['secondary_gadget']
        recon.melee = data['friendly']['recon']['melee']
        recon.collection_slot = 3
        recon.collection_id = friendly_kit.id
        recon.appearance = data['friendly']['recon']['appearance']
        recon.kit_asset = data['friendly']['recon']['kit_asset']
        recon.save()

    friendly_kit.save()



    enemy_kit : models.SoldierKitCollection = models.SoldierKitCollection.objects.filter(level_id = level_id, project_id = project_id, faction = 1).first()
    if not enemy_kit:
        enemy_kit : models.SoldierKitCollection = models.SoldierKitCollection.objects.create()
    enemy_kit.faction = 1
    enemy_kit.project_id = project_id
    enemy_kit.level_id = level_id
    
    if not enemy_kit.assault:
        assault : models.SoldierKit = models.SoldierKit.objects.create()
        assault.primary_weapon = data['enemy']['assault']['primary_weapon']
        # assault.primary_attachments = data['enemy']['assault']['primary_attachments']
        assault.secondary_weapon = data['enemy']['assault']['secondary_weapon']
        # assault.secondary_attachments = data['enemy']['assault']['secondary_attachments']
        assault.primary_gadget = data['enemy']['assault']['primary_gadget']
        assault.secondary_gadget = data['enemy']['assault']['secondary_gadget']
        assault.melee = data['enemy']['assault']['melee']
        assault.collection_slot = 0
        assault.collection_id = enemy_kit.id
        assault.appearance = data['enemy']['assault']['appearance']
        assault.kit_asset = data['enemy']['assault']['kit_asset']
        assault.save()
        enemy_kit.assault = assault
    else:
        assault : models.SoldierKit = models.SoldierKit.objects.filter(collection_slot = 0, collection_id = enemy_kit.id).first()
        assault.primary_weapon = data['enemy']['assault']['primary_weapon']
        # assault.primary_attachments = data['enemy']['assault']['primary_attachments']
        assault.secondary_weapon = data['enemy']['assault']['secondary_weapon']
        # assault.secondary_attachments = data['enemy']['assault']['secondary_attachments']
        assault.primary_gadget = data['enemy']['assault']['primary_gadget']
        assault.secondary_gadget = data['enemy']['assault']['secondary_gadget']
        assault.melee = data['enemy']['assault']['melee']
        assault.collection_slot = 0
        assault.collection_id = enemy_kit.id
        assault.appearance = data['enemy']['assault']['appearance']
        assault.kit_asset = data['enemy']['assault']['kit_asset']
        assault.save()

    if not enemy_kit.engineer:
        engineer : models.SoldierKit = models.SoldierKit.objects.create()
        engineer.primary_weapon = data['enemy']['engineer']['primary_weapon']
        # engineer.primary_attachments = data['enemy']['engineer']['primary_attachments']
        engineer.secondary_weapon = data['enemy']['engineer']['secondary_weapon']
        # engineer.secondary_attachments = data['enemy']['engineer']['secondary_attachments']
        engineer.primary_gadget = data['enemy']['engineer']['primary_gadget']
        engineer.secondary_gadget = data['enemy']['engineer']['secondary_gadget']
        engineer.melee = data['enemy']['engineer']['melee']
        engineer.collection_slot = 1
        engineer.collection_id = enemy_kit.id
        engineer.appearance = data['enemy']['engineer']['appearance']
        engineer.kit_asset = data['enemy']['engineer']['kit_asset']
        engineer.save()
        enemy_kit.engineer = engineer
    else:
        engineer : models.SoldierKit = models.SoldierKit.objects.filter(collection_slot = 1, collection_id = enemy_kit.id).first()
        engineer.primary_weapon = data['enemy']['engineer']['primary_weapon']
        # engineer.primary_attachments = data['enemy']['engineer']['primary_attachments']
        engineer.secondary_weapon = data['enemy']['engineer']['secondary_weapon']
        # engineer.secondary_attachments = data['enemy']['engineer']['secondary_attachments']
        engineer.primary_gadget = data['enemy']['engineer']['primary_gadget']
        engineer.secondary_gadget = data['enemy']['engineer']['secondary_gadget']
        engineer.melee = data['enemy']['engineer']['melee']
        engineer.collection_slot = 1
        engineer.collection_id = enemy_kit.id
        engineer.appearance = data['enemy']['engineer']['appearance']
        engineer.kit_asset = data['enemy']['engineer']['kit_asset']
        engineer.save()

    if not enemy_kit.support:
        support : models.SoldierKit = models.SoldierKit.objects.create()
        support.primary_weapon = data['enemy']['support']['primary_weapon']
        # support.primary_attachments = data['enemy']['support']['primary_attachments']
        support.secondary_weapon = data['enemy']['support']['secondary_weapon']
        # support.secondary_attachments = data['enemy']['support']['secondary_attachments']
        support.primary_gadget = data['enemy']['support']['primary_gadget']
        support.secondary_gadget = data['enemy']['support']['secondary_gadget']
        support.melee = data['enemy']['support']['melee']
        support.collection_slot = 2
        support.collection_id = enemy_kit.id
        support.appearance = data['enemy']['support']['appearance']
        support.kit_asset = data['enemy']['support']['kit_asset']
        support.save()
        enemy_kit.support = support
    else:
        support : models.SoldierKit = models.SoldierKit.objects.filter(collection_slot = 2, collection_id = enemy_kit.id).first()
        support.primary_weapon = data['enemy']['support']['primary_weapon']
        # support.primary_attachments = data['enemy']['support']['primary_attachments']
        support.secondary_weapon = data['enemy']['support']['secondary_weapon']
        # support.secondary_attachments = data['enemy']['support']['secondary_attachments']
        support.primary_gadget = data['enemy']['support']['primary_gadget']
        support.secondary_gadget = data['enemy']['support']['secondary_gadget']
        support.melee = data['enemy']['support']['melee']
        support.collection_slot = 2
        support.collection_id = enemy_kit.id
        support.appearance = data['enemy']['support']['appearance']
        support.kit_asset = data['enemy']['support']['kit_asset']
        support.save()
    
    if not enemy_kit.recon:
        recon : models.SoldierKit = models.SoldierKit.objects.create()
        recon.primary_weapon = data['enemy']['recon']['primary_weapon']
        # recon.primary_attachments = data['enemy']['recon']['primary_attachments']
        recon.secondary_weapon = data['enemy']['recon']['secondary_weapon']
        # recon.secondary_attachments = data['enemy']['recon']['secondary_attachments']
        recon.primary_gadget = data['enemy']['recon']['primary_gadget']
        recon.secondary_gadget = data['enemy']['recon']['secondary_gadget']
        recon.melee = data['enemy']['recon']['melee']
        recon.collection_slot = 3
        recon.collection_id = enemy_kit.id
        recon.appearance = data['enemy']['recon']['appearance']
        recon.kit_asset = data['enemy']['recon']['kit_asset']
        recon.save()
        enemy_kit.recon = recon
    else:
        recon : models.SoldierKit = models.SoldierKit.objects.filter(collection_slot = 3, collection_id = enemy_kit.id).first()
        recon.primary_weapon = data['enemy']['recon']['primary_weapon']
        # recon.primary_attachments = data['enemy']['recon']['primary_attachments']
        recon.secondary_weapon = data['enemy']['recon']['secondary_weapon']
        # recon.secondary_attachments = data['enemy']['recon']['secondary_attachments']
        recon.primary_gadget = data['enemy']['recon']['primary_gadget']
        recon.secondary_gadget = data['enemy']['recon']['secondary_gadget']
        recon.melee = data['enemy']['recon']['melee']
        recon.collection_slot = 3
        recon.collection_id = enemy_kit.id
        recon.appearance = data['enemy']['recon']['appearance']
        recon.kit_asset = data['enemy']['recon']['kit_asset']
        recon.save()

    enemy_kit.save()

    global_cache.level_model.friendly_kit = friendly_kit
    global_cache.level_model.enemy_kit = enemy_kit
    global_cache.level_model.save()
    
    return Response("Success")

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def manager_export_level(request : Request, project_id : int, level_id : int) -> Response:
    global global_cache
    level_object : navigation_models.Level = navigation_models.Level.objects.filter(project_id=project_id, level_id=level_id).first()
    level_data : dict = json.loads(JSONRenderer().render(serializers.LevelSerializer(level_object).data))
    with open(f'./models/Project/{level_object.project_id}/Level/{level_object.level_id}/level.json', 'w') as f:
        json.dump(level_data, f)
    return Response("Export")

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([AllowAny])
def manager_export_project(request : Request, project_id : int) -> Response:
    data = json.loads(JSONRenderer().render(serializers.ProjectSerializer(navigation_models.Project.objects.filter(project_id=project_id).first()).data))
    data['levels']= [json.loads(JSONRenderer().render(
            serializers.LevelSerializer(j).data
        )) for j in query.navigation_models.Level.objects.filter(project_id=project_id)]

    for idx, _ in enumerate(data['levels']):
        if data['levels'][idx]['friendly_kit']:
            data['levels'][idx]['friendly_kit'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitCollectionSerializer(models.SoldierKitCollection.objects.filter(id=data['levels'][idx]['friendly_kit'], faction=0).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['friendly_kit']['assault'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['friendly_kit']['id'], collection_slot=0).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['friendly_kit']['engineer'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['friendly_kit']['id'], collection_slot=1).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['friendly_kit']['support'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['friendly_kit']['id'], collection_slot=2).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['friendly_kit']['recon'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['friendly_kit']['id'], collection_slot=3).first()).data
            ).decode('utf-8'))
        if data['levels'][idx]['enemy_kit']:
            data['levels'][idx]['enemy_kit'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitCollectionSerializer(models.SoldierKitCollection.objects.filter(id=data['levels'][idx]['enemy_kit'], faction=1).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['enemy_kit']['assault'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['enemy_kit']['id'], collection_slot=0).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['enemy_kit']['engineer'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['enemy_kit']['id'], collection_slot=1).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['enemy_kit']['support'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['enemy_kit']['id'], collection_slot=2).first()).data
            ).decode('utf-8'))
            data['levels'][idx]['enemy_kit']['recon'] = json.loads(JSONRenderer().render(
                serializers.SoldierKitSerializer(models.SoldierKit.objects.filter(collection_id=data['levels'][idx]['enemy_kit']['id'], collection_slot=3).first()).data
            ).decode('utf-8'))
    
    with open(f"./models/Project/{navigation_models.Project.objects.filter(project_id=project_id).first().name}/project.json", "w") as f:
        json.dump(data, f)
    
    return Response(data)

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([AllowAny])
def manager_import_project(request : Request) -> Response:
    filename = request.data['filename']
    project_data : dict = {}
    with open(filename, 'r') as f:
        project_data = json.loads(f.read())
    
    project = navigation_models.Project.objects.create(
        name = project_data['name'],
        author = project_data['author'],
        date_created = project_data['date_created'],
        date_modified = project_data['data_modified'],
        description = project_data['description']
    )
    return Response('')

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_clear_assets(request : Request) -> Response:
    print("--- Deleting ALL assets ---")
    models.GameAsset.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute('vacuum;')
    return Response('Successfully deleted all assets.')

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_players(request : Request) -> Response:
    data = json.loads(JSONRenderer().render(serializers.PlayerSerializer(
            bots_models.Player.objects.all(), many=True
        ).data))
    for idx, player in enumerate(data):
        data[idx]['is_human'] = bots_models.Bot.objects.filter(player_id=player['player_id']).first() == None

    return Response(data)

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_record_player_path(request : Request, project_id : int) -> Response:
    data = request.data
    models.ProjectTaskJSON.objects.create(name='RecordPathTask', data=data, project_id=project_id, task_id = random.randint(0, 989988))
    return Response('Success')

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_on_recorded_path(request : Request, project_id : int) -> Response:
    global global_cache
    active_state : models.BF3GameManager = models.BF3GameManager.objects.first()
    if active_state:
        level_object = global_cache.get_object(active_state.active_project_id, active_state.active_level_id)
        if level_object:
            # do something here
            for task in models.ProjectTaskJSON.objects.filter(name='RecordPathTask').all():
                task : models.ProjectTaskJSON = task
                x = task.data['x']
                elevation = task.data['y']
                z = task.data['z']
                grid_pos = level_object.transform.transform_to_grid((x, z))
                best_layer = level_object.get_best_navmesh_level((grid_pos[0], grid_pos[1], elevation))
                if isinstance(global_cache.level_model.recorded_paths, list):
                    global_cache.level_model.recorded_paths.append({
                        'x': grid_pos[0], 'y': grid_pos[1], 'elevation': elevation, 'layer': best_layer
                    })
                    global_cache.level_model.save()
                else:
                    global_cache.level_model.recorded_paths = []
                    global_cache.level_model.save()

            models.ProjectTaskJSON.objects.filter(name='RecordPathTask').delete()
            with connection.cursor() as cursor:
                cursor.execute('vacuum;')
            print("Rasterizing")
            level_object.classify_costs(just_paths=True, elevation_based = True, elevation_alpha_power=2.0, elevation_alpha_beta=1.5, elevation_alpha_beta_power=1.0)
            global_cache.save_object()
            return Response("Success")
    return Response("Could not find active state or level", status=404)

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_add_spawn_point(request : Request, project_id : int, level_id : int, faction : int) -> Response:
    global global_cache
    if level_id == 99999999999999:
        level_id = models.BF3GameManager.objects.first().active_level_id
    print(request.data)
    
    level_object = global_cache.get_object(project_id, level_id)
    if level_object:
        point : dict = request.data
        point['y'] = point['y'] + 0.6

        spnts = global_cache.level_model.spawn_points_friendly if faction == 0 else global_cache.level_model.spawn_points_enemy
        if isinstance(spnts, list):
            spnts.append(request.data)
        else:
            spnts = [request.data]
        global_cache.level_model.use_spawn_points = True
        global_cache.level_model.save()
    return Response("Cannot find level.", status=404)

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_active_level_minimal(request : Request) -> Response:
    global global_cache
    settings : models.BF3GameManager = models.BF3GameManager.objects.first()
    global_cache.get_object(settings.active_project_id, settings.active_level_id)
    data =  serializers.LevelMinimalSerializer(navigation_models.Level.objects.filter(
        level_id = settings.active_level_id, project_id = settings.active_project_id).first()).data
    settings.reload = True
    settings.save()
    bots_models.Bot.objects.all().delete()
    bots_models.Player.objects.all().delete()
    print(data)
    return Response(data)