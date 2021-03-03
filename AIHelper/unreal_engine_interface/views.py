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
    image = Image.fromarray(((lm*255) / np.nanmax(lm[lm != np.inf])).astype(np.uint8), mode="L")
    response = HttpResponse(content_type='image/png')
    image.save(response, "PNG")
    return response