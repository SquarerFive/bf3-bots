from navigation import models as navigation_models
from manager import models
from rest_framework.authtoken.models import Token

from typing import Union, Tuple
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group

from datetime import datetime

def login_user(username: str, password: str) -> Tuple[bool, str]:
    profile = navigation_models.Profile.objects.filter(username=username).first()
    if profile:
        # print("Got profile: ", profile)
        user = authenticate(username=username, password=password)
        # print(user)
        if user != None:
            token = Token.objects.filter(user=user).first()
            if token:
                return (True, token.key)
            else:
                token = Token.objects.create(user=user)
                return (True, token.key)
    return (False, "")

def create_project(name : str, author_username: str, description : str = "") -> bool:
    profile = navigation_models.Profile.objects.filter(username=author_username).first()
    if profile:
        user = profile.user
        navigation_models.Project.objects.create(
            name=name, 
            project_id=navigation_models.Project.objects.count()+1, 
            date_created=datetime.now(),
            date_modified=datetime.now(),
            author=profile,
            description=description
        )