from django.shortcuts import render

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.renderers import JSONRenderer

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
    print("logging in", data)
    success, token = query.login_user(data['username'], data['password'])

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
    return Response(data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_level(request: Request, project_id: int, level_id: int):
    return Response(
        json.loads(JSONRenderer().render(serializers.LevelSerializer(
            query.navigation_models.Level.objects.filter(
                project_id=project_id, level_id=level_id).first()
        ).data)), content_type='application/json')


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
        image = Image.fromarray(((cost_surface*255) / np.max(cost_surface)).astype(np.uint8), mode="L")
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
    try:
        for level, value in enumerate(slot.values):
            levelObject.set_elevation_at(value['elevation'], slot.x, slot.y, level)
            levelObject.set_data_at(value['value'], slot.x, slot.y, level)
    except Exception as e:
        print(slot.values, e)
        # levelObject.set_elevation_at(slot.values[0][0]['elevation'], slot.x, slot.y)
        # levelObject.set_data_at(slot.values[0][0]['value'], slot.x, slot.y)

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
        levelObject.project_id = project_id
        levelObject.pre_process_data()
        navigation_query.encode_level(levelObject)
        levelModel = navigation_query.models.Level.objects.filter(project_id=project_id, name=level_name).first()


    levelModel = navigation_query.models.Level.objects.filter(project_id=project_id, name=level_name).first()
    d = models.ProjectTaskJSON.objects.create(
        level_id=levelModel.level_id,
        project_id=project_id,
        name='NavGridBuildTask',
        task_id=models.ProjectTaskJSON.objects.count()+1
    )
    d.data = data
    d.save()

    
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
    print('clearing level')
    if levelObject:
        levelObject.transform = transformObj
        levelObject.pre_process_data()
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
        return Response("Level reset successful")
    return Response("Level not found.", status=404)

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
    levelModel = navigation_query.models.Level.objects.filter(project_id=first_task.project_id, level_id=first_task.level_id).first()
    # levelObject = navigation_query.decode_level(levelModel)
    levelObject = global_cache.get_object(project_id, levelModel.level_id)
    for task in models.ProjectTaskJSON.objects.all():
        if levelModel.level_id != task.level_id or levelModel.project_id != task.project_id:
            levelObject.classify_costs()
            # navigation_query.encode_level(levelObject)
            global_cache.save_object()
            levelModel = navigation_query.models.Level.objects.filter(project_id=task.project_id, level_id=task.level_id).first()
            # levelObject = navigation_query.decode_level(levelModel)
            levelObject = global_cache.get_object(project_id, levelModel.level_id)
        for slot in task.data:
            push_level_block(LevelBlockInterface(slot), levelObject)
    levelObject.classify_costs()
    # navigation_query.encode_level(levelObject)
    global_cache.save_object()
    print('done')
    # for task in models.ProjectTaskJSON.objects.all():
    #     task.delete()
    return Response('Success')

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_add_level_feature(request: Request, project_id : int, level_id : int, feature_type: str):
    global global_cache
    level_model = navigation_query.models.Level.objects.filter(project_id=project_id, level_id=level_id).first()
    if feature_type == 'road':
        level_model.roads = json.loads(request.body.decode('utf-8'))
        level_model.save()
        print(level_model.roads, type(level_model.roads))
        #level_object = global_cache.get_object(project_id, level_id)
        # level_object = navigation_query.decode_level(level_model)
        # level_object.classify_costs()
        # navigation_query.encode_level(level_object)
        #global_cache.save_object()
    return Response('Success')

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([AllowAny])
def manager_update_level(request: Request, project_id : int) -> Response:
    global global_cache
    data = json.loads(request.body.decode('utf-8'))
    level_name = str(request.headers['Level'])
    level_model = level.models.Level.objects.filter(name=level_name, project_id=project_id).first()
    if level_model:
        level_object = global_cache.get_object(project_id, level_model.level_id)
        for objective in data['objectives']:
            navigation_query.add_objective(objective)
        for bot in data['bots']:
            bots_query.create_or_update_bot(bot)
            behaviour.compute(bot['bot_index'], level_object, bots_models.Bot, bots_models.Player, navigation_models.Objective)
        for player in data['players']:
            bots_query.create_or_update_player(player)
        data = {
            "bots" : bots_query.get_bots_as_dict()
        }
        response_data = json.dumps(data)
        # print(response_data)
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
@permission_classes([AllowAny])
def manager_clear_tasks(request : Request) -> Response:
    for task in models.ProjectTaskJSON.objects.all():
        task.delete()
    return Response("Done!")

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def manager_recalculate_costs(request : Request, project_id : int, level_id : int) -> Response:
    global global_cache
    level_object = global_cache.get_object(project_id, level_id)
    if level_object:
        level_object.classify_costs()
        global_cache.save_object()
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
            # print(is_us, is_ru)
            models.GameAsset.objects.create(name=asset_name, path=asset_path, asset_type=data['Category'][index], asset_team=asset_team)

    return Response("Success")

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_get_assets(request : Request) -> Response:
    assets = []
    for asset in models.GameAsset.objects.all():
        assets.append(
            json.loads(
                JSONRenderer().render(serializers.GameAssetSerializer(
                    asset
                ).data).decode('utf-8')
        ))
    return Response(assets)# content_type='application/json')