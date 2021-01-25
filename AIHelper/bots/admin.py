from django.contrib import admin
from .models import Player, Bot, BasePlayer
# Register your models here.

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    fields = ("name", "player_id", "team", "action", "order", "health", "transform", "in_vehicle", "path", "bot_index", "target", "squad")

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    fields = ("name", "player_id", "team", "health", "transform", "in_vehicle",  "has_soldier", "squad")
