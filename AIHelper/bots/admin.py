from django.contrib import admin
from .models import Player, Bot, BasePlayer
# Register your models here.

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ("name", "player_id", "action", "order", "team", "in_vehicle", 'stuck', 'health_provider', 'ammo_provider', 'target_vehicle', 'in_vehicle_turret', 'target_vehicle_slot')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    fields = ("name", "player_id", "team", "health", "transform", "in_vehicle",  "has_soldier", "squad")
    list_display = ("name", "player_id", "team", "in_vehicle", 'in_vehicle_turret', 'is_driver')

