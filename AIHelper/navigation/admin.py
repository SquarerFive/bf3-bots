from django.contrib import admin
from .models import Level, Objective, Profile, Project, Vehicle
# Register your models here.

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    fields = ("name","transform", "project_id", "date_created", "date_modified", "level_id", "roads", "structures", "recorded_paths", "spawn_points_friendly", "spawn_points_enemy", "use_spawn_points",
        "has_distance_field", "layers", "distance_field_threshold")

@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    fields = ("name", "index", "team", "attackingTeam", "transform", "controlled")
    list_display = ("name", "team", "controlled", "attackingTeam")

@admin.register(Profile)
class UserAdmin(admin.ModelAdmin):
    fields = ("username", "profile_id", "user_level", "user")

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    fields = ("project_id", "name", "author", "date_created", "date_modified", "description")

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    fields = ("instance", "vehicle_type", "transform", "passengers", "max_passenger_count")
    list_display = ("instance", "vehicle_type", "passengers", "max_passenger_count")