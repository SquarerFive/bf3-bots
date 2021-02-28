from django.contrib import admin
from .models import Level, Objective, Profile, Project, Vehicle, VehicleType
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
    fields = ("instance", "vehicle_type", "transform", "passengers", "max_passenger_count", "abstract_type")
    list_display = ("instance", "vehicle_type", "passenger_count", "max_passenger_count", "controllable_type", "abstract_type")

    def passenger_count(self, obj):
        count = 0
        for p in obj.passengers:
            if p != -1:
                count += 1
        return count

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    fields = ("controllable_type", "abstract_type", "turret_slots", "max_players", "can_drive_in_water")
    list_display = ("controllable_type", "abstract_type", "max_players", "can_drive_in_water")