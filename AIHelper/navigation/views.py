from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import json

import numpy as np
from .utilities import level
from .utilities import thread_pool
from .utilities import query, fast_stream
from bots.utilities import query as bot_query
from bots.utilities import behaviour
import bots.models as bot_models
from . import models as this_models
from PIL import Image
import time
# Create your views here.

current_level = None 
# work_thread_pool = thread_pool.ThreadPool()

@csrf_exempt
def index(request : HttpRequest) -> HttpResponse :
    global current_level
    #print(request.headers)
    data = request.body.decode("utf-8")
    with open("cache.json", "w") as f:
        f.write(data)
    data = json.loads(data)
    if not current_level:
        current_level = level.Level(
            str(request.headers['name']),
            ((float(request.headers['Min-X'].replace("'", "")), float(request.headers['Min-Y'].replace("'", ""))),
            (float(request.headers['Max-X'].replace("'", "") ), float(request.headers['Max-Y'].replace("'", ""))),
            int(float(str(request.headers['Size-X']).replace("'", ""))),
            int(float(str(request.headers['Size-Y']).replace("'","") ))),
            data
            )

        current_level.process_data()
        query.encode_level(current_level)

        # current_level.astar(
        #     current_level.transform.transform_to_grid((-128, 145)),
        #     current_level.transform.transform_to_grid((339, 257))
        # )
    else:
        #current_level.process_data()
        current_level.astar(
            current_level.transform.transform_to_grid((-128, 145)),
            current_level.transform.transform_to_grid((339, 257))
        )
        #work_thread_pool.enqueue(
        #    lambda: current_level.process_data()
        #)
    #print(len(data))
    return HttpResponse("Worked!")

@csrf_exempt
def test(request: HttpRequest):
    print(request.body)
    print(request.POST)
    return HttpResponse("Test")

@csrf_exempt
def update_level(request: HttpRequest) -> HttpResponse:
    global current_level
    ts = time.time()
    data = request.body.decode("utf-8")
    # print(data)
    data = json.loads(data)

    if not current_level:
        current_level = query.get_level_from_name(data['level_name'])
        if current_level:
            current_level.post_process_data()
    if current_level:
        for obj in data['objectives']:
            query.add_objective(obj)
        for bot in data['bots']:
            bot_query.create_or_update_bot(bot)
            #behaviour.global_behaviour_thread.enqueue(
            #    lambda : behaviour.compute(bot['bot_index'], current_level, bot_models.Bot, bot_models.Player, this_models.Objective)
            #)
            #behaviour.compute(bot['bot_index'], current_level)

        for player in data['players']:
            bot_query.create_or_update_player(player)

    data = {
        "bots": bot_query.get_bots_as_dict()
    }
    r=  json.dumps(data)
    # print('my data', r)
    # fast_stream.g_GlobalCache.result = r
    # fast_stream.start_socket_thread(r)
    # data = {
    #     'stream_length': len(fast_stream.g_GlobalCache.result),
    #     'any_data': len(fast_stream.g_GlobalCache.result) > 0,
    #     'port': fast_stream.socket_app.port
    # }
    # print("port: ", fast_stream.socket_app.port)
    
    # print(len(data['bots']))
    # print(data)
    te = time.time()
    #print(te-ts)
    return HttpResponse(r)


def update_level_socket(data : str) -> str:
    global current_level
    
    # data = request.body.decode("utf-8")
    # print(data)
    ts = time.time()
    data = json.loads(data)

    if not current_level:
        current_level = query.get_level_from_name(data['level_name'])
        if current_level:
            current_level.post_process_data()
    if current_level:
        for obj in data['objectives']:
            query.add_objective(obj)
        for bot in data['bots']:
            bot_query.create_or_update_bot(bot)
            #behaviour.global_behaviour_thread.enqueue(
            #    lambda : behaviour.compute(bot['bot_index'], current_level)
            #)
            #behaviour.compute(bot['bot_index'], current_level)

        for player in data['players']:
            bot_query.create_or_update_player(player)

    data = {
        "bots": bot_query.get_bots_as_dict()
    }
    te = time.time()
    return json.dumps(data)

@csrf_exempt
def find_path(request: HttpRequest) -> HttpResponse:
    global current_level
    start =  request.headers['Start']
    end =  request.headers['End']
    name = request.headers['Level-Name']
    grid_space = bool(request.headers['Grid-Space']=='true')
    print(bool(request.headers['Grid-Space']=='true'))
    start = start.split(",")
    start = (float(start[0]), float(start[1]))
    end = end.split(",")
    end = (float(end[0]), float(end[1]))
    print('end:', end)
    if current_level:
        if grid_space:
            d = current_level.astar(
                (int(start[0]), int(start[1])),
                (int(end[0]), int(end[1]))
            )
        else:
            d = current_level.astar(
                current_level.transform.transform_to_grid((start[0], start[1])),
                current_level.transform.transform_to_grid((end[0], end[1]))
            )
        d = json.dumps(d)
        return HttpResponse(d)
    else:
        current_level = query.get_level_from_name(name)
        if current_level:
            current_level.post_process_data()
            if grid_space:
                d = current_level.astar(
                    (int(start[0]), int(start[1])),
                    (int(end[0]), int(end[1]))
                )
            else:
                d = current_level.astar(
                    current_level.transform.transform_to_grid((start[0], start[1])),
                    current_level.transform.transform_to_grid((end[0], end[1]))
                )
            d = json.dumps(d)
            return HttpResponse(d)
        else:
            print("Level is not stored in DB!")

    return HttpResponse("Error, no level")

@csrf_exempt
def render_cost_surface(request: HttpRequest) -> HttpResponse:
    global current_level
    if not current_level:
        return HttpResponse("No level currently available. Please run !scorecard_bounds -x y -z x y z")
    image = Image.fromarray((current_level.costs*255).astype(np.uint8), mode="L")
    response = HttpResponse(content_type='image/png')
    image.save(response, "PNG")
    return response

@csrf_exempt
def export(request: HttpRequest) -> HttpResponse:
    global current_level
    if not current_level:
        return HttpResponse("No level currently available. Please run !scorecard_bounds -x y -z x y z")
    current_level.export()
    return HttpResponse("Success")

@csrf_exempt
def import_data(request: HttpRequest) -> HttpResponse:
    global current_level
    if not current_level:
        return HttpResponse("No level currently available. Please run !scorecard_bounds -x y -z x y z")
    name = request.headers['Level-Name']
    data_name = request.headers['Name']
    data_type = request.headers['Type']
    current_level.import_data(data_name, data_type)
    query.encode_level(current_level)
    return HttpResponse("Successful import")

@csrf_exempt
def modify_cost_surface(request : HttpRequest) -> HttpResponse:
    global current_level
    if not current_level:
        return HttpResponse("No level currently available. Please run !scorecard_bounds -x y -z x y z")
    position =  request.headers['Position']
    name = request.headers['Level-Name']
    recording_mode = request.headers['Recording-Mode']
    elevation = request.headers['Elevation']
    radius = request.headers['Sample-Radius']

    position = position.split(",")
    position = (float(position[0]), float(position[1]))
    # print("modify at ", position)
    current_level.modify(
        current_level.transform.transform_to_grid(position),
        recording_mode, elevation, float(radius)
    )
    return HttpResponse("Hello")

@csrf_exempt
def emit_action(request : HttpRequest) -> HttpResponse:
    global current_level
    if not current_level:
        return HttpResponse("No level currently available. Please run !scorecard_bounds -x y -z x y z")
    instigator  : int = int(request.headers['Instigator'])
    order       : int = int(request.headers['Order'])
    action      : int = int(request.headers['Action'])
    bot_query.emit_and_propagate_action(instigator, order, action)
    return HttpResponse("Success")

@csrf_exempt
def close_faststream(request: HttpRequest) -> HttpResponse:
    fast_stream.stop_socket_thread()
    return HttpResponse("0")

@csrf_exempt
def render_level(request : HttpRequest, level_name : str) -> HttpResponse:
    
    return HttpResponse("H")

@csrf_exempt
def register_user(request : HttpRequest) -> HttpResponse:
    data = json.loads(request.body.decode('utf-8'))
    query.register_user(
        data['username'],
        data['email'],
        data['password'],
        data['description']
    )
    return HttpResponse("Success")


@login_required()
def auth_test(request : HttpRequest) -> HttpResponse:
    print(request.user.is_authenticated)
    return HttpResponse("Hello")