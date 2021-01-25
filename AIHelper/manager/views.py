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

import numpy as np
import pickle
import base64

from PIL import Image
from django.http import HttpResponse

from typing import List

from manager import models

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
    level = query.navigation_models.Level.objects.filter(project_id=project_id, level_id=level_id).first()
    if level:
        cost_surface = pickle.loads(base64.b64decode(level.cost_data))
        print(cost_surface.shape)
        image = Image.fromarray((cost_surface*255).astype(np.uint8), mode="L")
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
    new_level.process_data()
    new_level.post_process_data()
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
    levelObject.set_elevation_at(slot.elevation, slot.x, slot.y)
    levelObject.set_data_at(slot.values[0], slot.x, slot.y)

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_add_level_block(request : Request, project_id : int):
    data : List[LevelBlockInterface] = json.loads(request.body.decode('utf-8'))
    # list of { x: Int, y: Int, elevation: Float, values: Float[] }
    level_name = str(request.headers['Level'])
    levelModel = navigation_query.models.Level.objects.filter(project_id=project_id, name=level_name).first()
    levelObject = navigation_query.decode_level(levelModel)
    if not levelObject and levelModel:
        levelObject = level.Level(level_name, ((float(request.headers['Min-X'].replace("'", "")), float(request.headers['Min-Y'].replace("'", ""))),
            (float(request.headers['Max-X'].replace("'", "") ), float(request.headers['Max-Y'].replace("'", ""))),
            int(float(str(request.headers['Size-X']).replace("'", ""))),
            int(float(str(request.headers['Size-Y']).replace("'","") ))), None)
        levelObject.pre_process_data()
        navigation_query.encode_level(levelObject)
        
    levelModel = navigation_query.models.Level.objects.filter(project_id=project_id, name=level_name).first()
    d = models.ProjectTaskJSON.objects.create(
        level_id=levelModel.level_id,
        project_id=project_id,
        name='NavGridBuildTask'
    )
    d.data = data
    d.save()

    
    if levelObject and levelModel:
        for slot in data:
           push_level_block(LevelBlockInterface(slot), levelObject)
        levelObject.classify_costs()
        navigation_query.encode_level(levelObject)
    else:
        levelObject = level.Level(level_name, ((float(request.headers['Min-X'].replace("'", "")), float(request.headers['Min-Y'].replace("'", ""))),
            (float(request.headers['Max-X'].replace("'", "") ), float(request.headers['Max-Y'].replace("'", ""))),
            int(float(str(request.headers['Size-X']).replace("'", ""))),
            int(float(str(request.headers['Size-Y']).replace("'","") ))), None)
        levelObject.pre_process_data()
        for slot in data:
            push_level_block(LevelBlockInterface(slot), levelObject)
        # levelObject.classify_costs()
        navigation_query.encode_level(levelObject)
    return Response('Success!')

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_complete_level_block(request: Request, project_id : int) -> Response:
    level_name = str(request.headers['Level'])
    # all we need to do is complete the rasterization
    levelModel = navigation_query.models.Level.objects.filter(project_id=project_id, name=level_name).first()
    levelObject = navigation_query.decode_level(levelModel)
    if levelObject:
        levelObject.classify_costs()
        navigation_query.encode_level(levelObject)
    else:
        return Response('Failed to find level', status=404)
    return Response('Success!')

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def manager_clear_level_data(request : Request, project_id : int) -> Response:
    level_name = str(request.headers['Level'])
    levelModel = navigation_query.models.Level.objects.filter(project_id=project_id, name=level_name).first()
    levelObject = navigation_query.decode_level(levelModel)
    transform = ((float(request.headers['Min-X'].replace("'", "")), float(request.headers['Min-Y'].replace("'", ""))),
            (float(request.headers['Max-X'].replace("'", "") ), float(request.headers['Max-Y'].replace("'", ""))),
            int(float(str(request.headers['Size-X']).replace("'", ""))),
            int(float(str(request.headers['Size-Y']).replace("'","") )))
    transformObj = level.transformations.GridTransform(transform[0], transform[1], transform[2], transform[3])
    if levelObject:
        levelObject.transform = transformObj
        levelObject.pre_process_data()
        navigation_query.encode_level(levelObject)
    else:
        print('failed to find level :(')
        return Response('Failed to find level.', status=404)
    return Response('Success!')