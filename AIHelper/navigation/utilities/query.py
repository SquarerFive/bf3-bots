from navigation import models
from . import level
from . import transformations

import pickle
import base64

from typing import Union
import datetime

from django.contrib.auth.hashers import Argon2PasswordHasher

from django.contrib.auth.models import User, Group
from django.http import HttpRequest, HttpResponseRedirect
from django.contrib.auth import authenticate, login

def encode_level(in_level : level.Level) -> None:
    data_bytes = pickle.dumps(in_level.data)
    data_bytes_b64 = base64.b64encode(data_bytes)
    costs_bytes = pickle.dumps(in_level.costs)
    costs_bytes_b64 = base64.b64encode(costs_bytes)
    elevation_bytes = pickle.dumps(in_level.elevation)
    elevation_bytes_b64 = base64.b64encode(elevation_bytes)
    l = models.Level.objects.filter(project_id = in_level.project_id).first()
    l_id = models.Level.objects.filter(project_id = in_level.project_id).count() + 1
    if not l:
        l = models.Level(raw_data=data_bytes_b64, cost_data=costs_bytes_b64, elevation_data=elevation_bytes_b64, name=in_level.name, project_id=in_level.project_id, level_id=l_id)
    else:
        l.raw_data = data_bytes_b64
        l.cost_data = costs_bytes_b64
        l.elevation_data = elevation_bytes_b64
    l.transform = in_level.transform.as_dict()
    l.save()

def decode_level(in_data : models.Level) -> Union[level.Level, None]:
    if not in_data: return None

    data_bytes = base64.b64decode(in_data.raw_data)
    costs_bytes = base64.b64decode(in_data.cost_data)
    elevation_bytes = base64.b64decode(in_data.elevation_data)

    data = pickle.loads(data_bytes)
    costs = pickle.loads(costs_bytes)
    elevation = pickle.loads(elevation_bytes)
    transform = transformations.from_dict(in_data.transform)
    l = level.Level(in_data.name)
    l.data = data
    l.costs = costs
    l.elevation = elevation
    l.transform = transform
    l.project_id = in_data.project_id
    return l

def get_level_from_name(name : str) -> Union[level.Level, None]:
    return decode_level(models.Level.objects.filter(name=name).first())

def add_objective(data : dict):
    if not models.Objective.objects.filter(name=data['name']).first():
        o = models.Objective(index=data['index'], team=data['team'], attackingTeam=data['attackingTeam'], name=data['name'])
        o.transform = data['transform']
        o.controlled = bool(data['controlled'])
        o.save()
    else:
        o = models.Objective.objects.filter(name=data['name']).first()
        o.team = data['team']
        o.attackingTeam = data['attackingTeam']
        o.index = data['index']
        o.controlled = bool(data['controlled'])
        o.save()

# wouldn't want xss attack, would you?
def filter_text(text : str):
    return text.replace("<", "&#60;").replace(">", "&#62;")

# don't use your primary password
def register_user(
    username: str,
    email: str,
    password: str,
    description: str,):
    # ensure unique
    if models.Profile.objects.filter(username=username).first() == None:
        models.Profile.objects.create(
            user_level = 0, 
            profile_id = models.Profile.objects.count()+1,
            username = username,
            user = User.objects.create(username=username, password=password, email=email),
            description = description)