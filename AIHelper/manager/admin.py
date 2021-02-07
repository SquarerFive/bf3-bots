from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.ProjectTaskJSON)
class ProjectTaskJSONAdmin(admin.ModelAdmin):
    fields = ("name", "task_id", "level_id", "project_id", "data")

@admin.register(models.GameAsset)
class GameAssetAdmin(admin.ModelAdmin):
    fields = ("name", "path", 'asset_type')

@admin.register(models.SoldierKit)
class SoldierKitAdmin(admin.ModelAdmin):
    fields = ('primary_weapon', 'secondary_weapon', 'primary_gadget', 'secondary_gadget', 'melee', 'kit_asset', 'appearance')

@admin.register(models.SoldierKitCollection)
class SoldierKitCollectionAdmin(admin.ModelAdmin):
    fields = ('assault', 'engineer', 'support', 'recon', 'faction')