from . import transformations
from . import scorecard
from .. import models

import numpy as np
from matplotlib import pyplot
from skimage.graph import route_through_array, shortest_path
import math

# from pathfinding.core.diagonal_movement import DiagonalMovement
# from pathfinding.core.grid import Grid
# from pathfinding.finder.a_star import AStarFinder
# from pathfinding.finder.dijkstra import DijkstraFinder
# from pathfinding.finder.best_first import BestFirst
# from pathfinding.finder.ida_star import IDAStarFinder
# from pathfinding.finder.bi_a_star import BiAStarFinder

from . import astar

from typing import Union
import copy
import pyastar

import datetime

class Level:
    def __init__(self, name, transform : Union[tuple, None] = None, data: list = [], model : Union[None, models.Level] = None):
        self.raw_data = data
        if transform:
            self.transform = transformations.GridTransform(transform[0], transform[1], transform[2], transform[3])
        self.data = None
        self.elevation = None
        self.costs = None
        self.costs_canvas = None
        self.costs_preview = None
        self.name = name
        self.grid = None

        self.project_id = 0

        self.model = model

    def classify_costs(self):
        scorecard.Scorecard.score(self.model, self.transform, self.data, self.elevation, self.costs)

    # Call this after initialising Level
    def pre_process_data(self):
        _width = self.transform.width+1
        _height = self.transform.height + 1

        print("Creating arrays with size: ", _width, _height)
        self.data = np.zeros((10, _width, _height))
        self.elevation = np.zeros((10, _width, _height))
        self.costs = np.zeros((10, _width, _height))
        self.costs_canvas = np.zeros((10, _width, _height))
    
    def sensecheck(self):
        try:
            print(self.transform.width)
            print(self.transform.height)
            if self.data.shape[1] < self.transform.width+1:
                print("Sensecheck failed, recreating array.")
                self.pre_process_data()
        except:
            print("No array found, reinitialising.")
            self.pre_process_data()

    def process_data(self):
        print("Processing data")
        _width = len(self.raw_data)
        _height = len(self.raw_data[0])
        
        for x in range(_width):
            for y in range(_height):
                self.data[y][x] = self.raw_data[x][y][0]
                self.elevation[y][x] = self.raw_data[x][y][1]
        scorecard.Scorecard.score(self.model, self.transform, self.data, self.elevation, self.costs)

        fig = pyplot.figure(frameon=False)
        img = pyplot.imshow(self.costs)
        pyplot.axis("off")
        
        pyplot.savefig("./wake_island_cstf.png", bbox_inches='tight')
        self.post_process_data()

    def set_elevation_at(self, value : float, index_x : int, index_y : int, level : int = 0):
        try:
            self.elevation[level][index_y-1][index_x-1] = value
        except Exception as e:
            print(index_x-1, index_y-1)
            raise(e)

    def set_data_at(self, value : int, index_x : int, index_y : int, level : int = 0):
        try:
            self.data[level][index_y-1][index_x-1] = value
        except Exception as e:
            print(level, index_x-1, index_y-1)
            raise(e)

    def post_process_data(self):
        # scorecard.Scorecard.score(self.data, self.costs)
        if not self.grid:
            # self.grid = Grid(matrix = self.costs)
            self.transform.width = self.costs.shape[0]
            self.transform.height = self.costs.shape[1]

    def get_valid_point_in_radius(self, arr : np.ndarray, x: int, y : int, radius: float = 10.0) -> list:
        if arr[0][x][y] == 1.0:
            return (x,y)
        offsets = [(-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1)]
        found = False
        # final
        final_pos = [x,y]
        min_s = math.inf
        for g in range(1, int(radius)):
            for offset in offsets:
                i = y+(offset[1]*g)
                j = x+(offset[0]*g)
                score = arr[0][j][i]-self.elevation[0][j][i]
                if arr[0][j][i] != np.inf and score < min_s and score > 0.0:
                    found = True
                    final_pos = [j, i]
                    min_s = score
            #if found:
            #    break
        return final_pos


    # def find_path(self, start: tuple, end : tuple) -> list:
    #     
    #     self.grid.cleanup()
    #     start = self.grid.node(start[0], start[1])
    #     end = self.grid.node(end[0], end[1])
    #     finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    #     path, runs = finder.find_path(start, end, self.grid)
    #     path = [(p[1], p[0]) for p in path]
    #     return path

    def find_path_safe(self, start: tuple, end: tuple) -> list:
        #print(self.costs)
        #grid = self.grid
        #grid.cleanup()
        #start = grid.node(start[0], start[1])
        #end = grid.node(end[0], end[1])
        #finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        #path, runs = finder.find_path(start, end, grid)
        # print(start, end)
        #print(self.costs[start[0]][start[1]])
        #print(self.costs[end[0]][end[1]])
        # print(self.costs[start[0]][[start[1]]])
        # print(self.costs[end[0]][[end[1]]])
        #path = astar.astar(self.costs, start, end)
        #print('astar: ', start, end)
        path = pyastar.astar_path(self.costs[0], start, end, allow_diagonal=True)
        #print(path)
        # path = [(p[1], p[0]) for p in path]
        # grid.__del
        return path

    def astar(self, start : tuple, end : tuple, safe=True , all : bool = False) -> list:
        # print("running astar  ", start, end)
        # print("size of data: ", self.data.shape)
        #path, cost = route_through_arrays(self.costs, start, end, fully_connected=False, geometric=True) # astar(self.data, start, end)
        #if not safe:
        #    path = self.find_path(start, self.get_valid_point_in_radius(self.costs, end[0], end[1], 10))
        #else:
        # return []
        # print('finding path', start, end)
        if (start[0] > 0 and start[0] < self.costs.shape[1] and start[1] > 0 and start[1] < self.costs.shape[2]
            and end[0] > 0 and end[0] < self.costs.shape[1] and end[1] > 0 and end[1] < self.costs.shape[2]):
                path = self.find_path_safe(
                    self.get_valid_point_in_radius(self.costs, start[0], start[1], 5), 
                    self.get_valid_point_in_radius(self.costs, end[0], end[1], 5))
        else:
            return []
        #print('got path')
        #path = astar(self.costs, start, end)
        # path_and_cost = [(p[0], p[1], self.costs[p[0]][p[1]] ) for p in path]
        world_paths = []
        if type(path) != type(None):
            for idx, p in enumerate(path):
                # self.costs_preview[p[0]][p[1]] = 0.5
                wxy = self.transform.transform_to_world(p)
                world_paths.append({
                    "x": wxy[0],
                    "y": self.elevation[0][p[0]][p[1]]+1,
                    "z": wxy[1]
                })
                if idx > 50:
                    break
        else:
            None

        # print(world_paths)
        # data = np.copy(self.costs)
        # 
        # 
        # for point in path:
        #     x = int(point[0])
        #     y = int(point[1])
        #     data[x][y] = 0.0
        # fig = pyplot.figure(frameon=False)
        # img = pyplot.imshow(data)
        # pyplot.axis("off")
        # np.save("./wake_island_data.data", self.data)
        # np.save("./wake_island_path.data", data)
        # pyplot.savefig("./wake_island_path.png", bbox_inches='tight')

        return world_paths#[0:128]# [0: min((len(world_paths)-1), 20)]
    
    def export(self):
        file_name = "./exports/<context>"+datetime.datetime.now().strftime("%d-%m-%Y")
        np.save(file_name.replace("<context>", "costs"), self.costs)
        np.save(file_name.replace("<context>", "costs_canvas"), self.costs_canvas)
        np.save(file_name.replace("<context>", "data"), self.data)
        np.save(file_name.replace("<context>", "elevation"), self.elevation)
    
    

    def import_data(self, data_name: str, data_type: str):
        with open(f"./exports/{data_name}", "rb") as f:
            if data_type == "costs":
                self.costs = np.load(f)
                #scorecard.flip_scorecard(np.load(f), self.costs)
                self.costs = self.costs.astype(np.float32)
                self.costs_preview = np.copy(self.costs)

            elif data_type == "costs_canvas":
                #self.costs_canvas = np.load(f)
                scorecard.flip_scorecard(np.load(f), self.costs_canvas)
            elif data_type == "data":
                #self.data = np.load(f)
                scorecard.flip_scorecard(np.load(f), self.data)
            elif data_type == "elevation":
                try:
                    self.elevation = np.load(f)
                except Exception as e:
                    print("Failed to load elevation!! ", e)
                #scorecard.flip_scorecard(np.load(f), self.elevation)

    def modify(self, grid_position : tuple, recording_mode: float, elevation: float, radius : float):
        recording_mode = float(recording_mode)
        value = 1.0
        if recording_mode == 1.0:
            #value = 0.0
            value = np.inf
        if type(self.costs_canvas) == type(None):
            self.costs_canvas = np.zeros((self.costs.shape[0], self.costs.shape[1]))
        for x in range(-1,2):
            for y in range(-1, 2):
                self.costs_preview[grid_position[0]+x][grid_position[1]+y] = 25
        #print("Modifing at ", grid_position, recording_mode, value)
        for x in range(-16, 16):
            for y in range(-16, 16):
                if math.sqrt(x**2+y**2) < radius:
       
                    self.costs_canvas[grid_position[0]+x][grid_position[1]+y] = value
                    self.costs[grid_position[0]+x][grid_position[1]+y] = value
                    self.elevation[grid_position[0]+x][grid_position[1]+y] = elevation

        #print(self.costs[grid_position[0]][grid_position[1]])
    