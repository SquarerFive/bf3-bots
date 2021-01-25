from rest_framework import serializers
from navigation import models as navigation_models

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
        exclude = ['raw_data', 'cost_data', 'elevation_data']