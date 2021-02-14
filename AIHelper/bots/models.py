from django.db import models

# Create your models here.

class BasePlayer(models.Model):
    player_id = models.IntegerField(default=0)
    name = models.CharField(max_length=128, default="BattlefieldBoomer1234")
    
    online_id = models.IntegerField(default=0)

    alive = models.BooleanField(default=False)
    is_squad_leader = models.BooleanField(default = False)
    is_squad_private = models.BooleanField(default = False)
    transform = models.JSONField(default=dict)
    in_vehicle = models.BooleanField(default=False)

    has_soldier = models.BooleanField(default = False)
    team = models.IntegerField(default = 0)
    squad = models.IntegerField(default = 0)

    health = models.IntegerField(default=100)

    class Meta:
        abstract = True

class Bot(BasePlayer):
    bot_index = models.IntegerField(default = 1) # index in botManager table
    action = models.IntegerField(default=2)
    order  = models.IntegerField(default=2)
    path = models.JSONField(default=dict, blank=True, null=True)
    target = models.IntegerField(default = -1)
    overidden_target = models.IntegerField(default = -2)
    selected_kit = models.JSONField(default = dict)

    last_transform = models.JSONField(default=dict, null=True, blank=True)
    last_transform_update = models.DateTimeField(auto_created=True, editable=True)
    
    stuck = models.BooleanField(default=False)

    
class Player(BasePlayer):
    pass
    
    
   