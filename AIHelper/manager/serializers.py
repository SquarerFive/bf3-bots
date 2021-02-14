from rest_framework import serializers
from navigation import models as navigation_models
from bots import models as bots_models
from . import models

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = navigation_models.Profile
        exclude = ['user']


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(many=False)
    class Meta:
        model = navigation_models.Project
        fields = '__all__'

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = navigation_models.Level
        fields = '__all__'
        # exclude = ['raw_data', 'cost_data', 'elevation_data']

class ProjectTaskJSONSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProjectTaskJSON
        exclude = ['data']

class GameAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GameAsset
        fields = '__all__'

class SoldierKitCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SoldierKitCollection
        fields = '__all__'

class SoldierKitSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SoldierKit
        fields = '__all__'

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = bots_models.Player
        fields = '__all__'