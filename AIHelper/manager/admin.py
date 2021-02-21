from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.ProjectTaskJSON)
class ProjectTaskJSONAdmin(admin.ModelAdmin):
    fields = ("name", "task_id", "level_id", "project_id", "data")

@admin.register(models.GameAsset)
class GameAssetAdmin(admin.ModelAdmin):
    fields = ("name", "path", 'asset_type', "tags")
    list_display = ("name", "path", "asset_type", "tags")

@admin.register(models.SoldierKit)
class SoldierKitAdmin(admin.ModelAdmin):
    fields = ('primary_weapon', 'secondary_weapon', 'primary_gadget', 'secondary_gadget', 'melee', 'kit_asset', 'appearance')

@admin.register(models.SoldierKitCollection)
class SoldierKitCollectionAdmin(admin.ModelAdmin):
    fields = ('assault', 'engineer', 'support', 'recon', 'faction', 'project_id', 'level_id')
    list_display = ['project_id', 'level_id', 'faction']

@admin.register(models.BF3GameManager)
class BF3GameManagerAdmin(admin.ModelAdmin):
    fields = ('active_project_id', 'active_level_id')
    list_display = ['active_project_id', 'active_level_id']