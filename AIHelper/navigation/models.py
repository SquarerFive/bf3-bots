from django.db import models
import django.contrib.auth.models as django_models
from manager.models import SoldierKitCollection

# Create your models here. 

class Objective(models.Model):
    index = models.IntegerField(default=0)
    team = models.IntegerField(default=0)
    attackingTeam = models.IntegerField(default=0)
    transform = models.JSONField()
    name = models.CharField(max_length=24)
    controlled = models.BooleanField(default=False)
    capturable = models.BooleanField(default=True)

class Level(models.Model):
    # raw_data = models.BinaryField(blank=True, null=True)
    # cost_data = models.BinaryField(blank=True, null=True)
    # elevation_data = models.BinaryField(blank=True, null=True)

    relative_path = models.TextField(default="./models/Project/{0}/Level/{1}/")

    name = models.TextField(default="no-map-name")
    transform = models.JSONField(default=dict, null=True)

    project_id = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_created=True, null=True)
    date_modified = models.DateTimeField(auto_created=True, null=True)

    level_id = models.IntegerField(default= 0)

    roads = models.JSONField(default = dict, null=True, blank=True)
    structures = models.JSONField(default = dict, null=True, blank=True)

    friendly_kit = models.ForeignKey(SoldierKitCollection, on_delete=models.CASCADE, related_name='friendly_kit', null=True)
    enemy_kit = models.ForeignKey(SoldierKitCollection, on_delete=models.CASCADE, related_name='enemy_kit', null=True)
    recorded_paths = models.JSONField(default=list, null=True, blank=True)

    spawn_points_friendly = models.JSONField(default = list, null = True, blank = True) # f0
    spawn_points_enemy = models.JSONField(default = list, null = True, blank = True) # f1
    use_spawn_points = models.BooleanField(default=False)

    has_distance_field = models.BooleanField(default = True)
    layers = models.IntegerField(default = 10)

    distance_field_threshold = models.FloatField(default = 32)

class Project(models.Model):
    project_id = models.IntegerField(default = 0)
    name = models.TextField(default = "no-map-name")
    author = models.ForeignKey("Profile", on_delete=models.CASCADE, blank=True, null=True)
    date_created = models.DateTimeField(auto_created=True)
    date_modified = models.DateTimeField(auto_created=True)
    description = models.TextField(default="")

class Profile(models.Model):
    # 0 = guest
    # 1 = project Contributor [modify project levels, etc]
    # 2 = project Manager [add/delete/modify project/levels, remove or add contributor]
    # 3 = site admin
    user_level = models.IntegerField(default = 0) 
    profile_id = models.IntegerField(default = 0)
    username = models.TextField(default="")
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    description = models.CharField(default="", max_length=4000)
    session_token = models.TextField(null=True, blank=True)
    session_salt = models.TextField(null = True, blank=True)

    def __str__(self):
        return self.username

    def natural_key(self):
        return self.username
    
class Vehicle(models.Model):
    instance = models.TextField(default = "")
    passengers = models.JSONField(default=list) # List of player IDs
    max_passenger_count = models.IntegerField(default = 3)
    transform = models.JSONField(default = dict)
    vehicle_type = models.IntegerField(default = 0)
    controllable_type = models.TextField(default = "", null=True)
    
