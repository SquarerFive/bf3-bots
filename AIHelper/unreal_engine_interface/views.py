from typing import Union
from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.renderers import JSONRenderer

import json
from navigation import models as navigation_models
from navigation.utilities import level as navigation_level
from navigation.utilities import query as navigation_query
from navigation.utilities import scorecard as navigation_scorecard

from PIL import Image
import imageio
import numpy as np


# Create your views here.

class UnrealEngineDataInterface:
    def __init__(self):
        self.project_id = 0
        self.level_id = 0
        self.level: Union[navigation_level.Level, None] = None

    def get_level(self, project_id: int, level_id: int):
        if not self.level:
            level = navigation_models.Level.objects.filter(project_id=project_id, level_id=level_id).first()
            self.level = navigation_query.decode_level(level) 
        if self.level.model.level_id != level_id or self.level.model.project_id != project_id:
            level = navigation_models.Level.objects.filter(project_id=project_id, level_id=level_id).first()
            self.level = navigation_query.decode_level(level) 
        return self.level

UEDataIFace = UnrealEngineDataInterface()

#@ PRIMARY UTILITY

@api_view(['GET'])
@permission_classes([AllowAny])
def uei_gtm(request: Request, project_id: int, level_id: int) -> Response:
    global UEDataIFace
    level = UEDataIFace.get_level(project_id, level_id)
    lm = level.elevation.copy()[0]
    navigation_scorecard.mask_replace_with(
        lm, level.feature[0], 1, 0.0
    )
    r = ((lm*255) / np.nanmax(lm[lm != np.inf]))
    
    # image = Image.fromarray(((lm*255) / np.nanmax(lm[lm != np.inf])).astype(np.uint32), mode="L")
    image = Image.fromarray(r, mode="I")
    response = HttpResponse(content_type='image/png')
    image.save('../rasters/test.tif')
    imageio.imwrite('../rasters/test.png', r.astype(np.uint16))
    image.save(response, "PNG")
    return response

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([TokenAuthentication, SessionAuthentication])
def uei_gtp(request: Request, project_id: int, level_id: int) -> Response:
    global UEDataIFace
    level = UEDataIFace.get_level(project_id, level_id)
    data = request.data
    print(data)
    start_grid_pos = level.transform.transform_to_grid(
        (
            data['start'][0]/100, data['start'][1]/100
        )
    )
    end_grid_pos = level.transform.transform_to_grid(
        (
            data['end'][0]/100, data['end'][1]/100
        )
    )

    print(start_grid_pos, end_grid_pos)

    path = list(level.find_path_safe(start_grid_pos, end_grid_pos, 0, 0, True)[0])

    new_path = []
    for p in path:
        print(p)
        w = level.transform.transform_to_world((int(p[1]), int(p[0])))
        new_path.append(
            (w[0], w[1])
        )
    new_path.reverse()
    data = {'path': new_path}
    return Response(data, content_type='application/json')