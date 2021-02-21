from django.db import models

# Create your models here.


class ProjectTaskJSON(models.Model):
    name = models.TextField(default='DefaultTask')
    data = models.JSONField(null=True, blank=True, default=dict)
    project_id = models.IntegerField()
    level_id = models.IntegerField(default=-1)
    task_id = models.IntegerField(default=0)

class GameAsset(models.Model):
    name = models.TextField(default="MyObject")
    path = models.TextField(default='Path/ToObject')
    asset_type = models.TextField(default="Primary Weapon")
    asset_team = models.TextField(default="ALL")
    tags = models.JSONField(default=dict)
    children = models.JSONField(default=list)

class SoldierKit(models.Model):
    # JSON field contains all possible weapons for that slot
    primary_weapon = models.JSONField(default=dict) # 0
    # primary_attachments = models.JSONField(default=list) # 
    secondary_weapon = models.JSONField(default=dict) # 1
    # secondary_attachments = models.JSONField(default=list) # 
    primary_gadget = models.JSONField(default=dict) # 2 (engineer) 4 (support/assault)
    secondary_gadget = models.JSONField(default=dict) # 5
    melee = models.JSONField(default=dict) # 7

    collection_id = models.IntegerField(default=0)
    collection_slot = models.IntegerField(default = 0) # 0 = assault ... 3 = recon

    kit_asset = models.JSONField(default=dict)
    appearance = models.JSONField(default=list)

class SoldierKitCollection(models.Model):
    assault = models.ForeignKey(SoldierKit,     on_delete=models.CASCADE,   related_name='assault_kit', null=True)
    engineer = models.ForeignKey(SoldierKit,    on_delete=models.CASCADE,   related_name='engineer_kit', null=True)
    support = models.ForeignKey(SoldierKit,     on_delete=models.CASCADE,   related_name='support_kit', null=True)
    recon = models.ForeignKey(SoldierKit,       on_delete=models.CASCADE,   related_name='recon_kit', null=True)
    
    faction = models.IntegerField(default=0)

    project_id = models.IntegerField(default=0)
    level_id = models.IntegerField(default=0)

class BF3GameManager(models.Model):
    active_project_id = models.IntegerField(default=0)
    active_level_id = models.IntegerField(default=0)
    reload = models.BooleanField(default=False)