from django.db.models import query
from navigation import models as navigation_models
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from manager import serializers, models

class LevelViewset(viewsets.ModelViewSet):
    """
    A viewset used to retrieve or update levels.
    """

    serializer_class = serializers.LevelSerializer
    queryset = navigation_models.Level.objects.all()

class ProjectViewset(viewsets.ModelViewSet):
    """
    Viewset to retrieve or update projects.
    """

    serializer_class = serializers.ProjectSerializer
    queryset = navigation_models.Project.objects.all()

class SoldierKitCollectionViewset(viewsets.ModelViewSet):
    """
    Viewset that is used to retrieve or update soldier kit collections (assault, engineer, support, recon).
    """

    serializer_class = serializers.SoldierKitCollectionSerializer
    queryset = models.SoldierKitCollection.objects.all()