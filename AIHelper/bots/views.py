from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
import json

from .utilities import query

# Create your views here.

def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello")

@csrf_exempt
def register_bot(request: HttpRequest) -> HttpResponse:
    data = request.body.decode("utf-8")
    # print(data)
    data = json.loads(data)
    query.create_or_update_bot(data)
    return HttpResponse("Register Bot")