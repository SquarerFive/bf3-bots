from . import transformations
from . import scorecard
from .. import models

import numpy as np
from matplotlib import pyplot, use
from skimage.graph import route_through_array, shortest_path
import math
import simplification
from simplification.cutil import simplify_coords_idx

# from pathfinding.core.diagonal_movement import DiagonalMovement
# from pathfinding.core.grid import Grid
# from pathfinding.finder.a_star import AStarFinder
# from pathfinding.finder.dijkstra import DijkstraFinder
# from pathfinding.finder.best_first import BestFirst
# from pathfinding.finder.ida_star import IDAStarFinder
# from pathfinding.finder.bi_a_star import BiAStarFinder

from . import astar
from . import dffinding

from typing import List, Tuple, Union
import copy
import pyastar

import datetime

from numba import int32, float32
from numba.typed import List
class Level:
    def __init__(self, name, transform : Union[tuple, None] = None, data: list = [], model : Union[None, models.Level] = None):
        self.raw_data = data
        if transform:
            self.transform = transformations.GridTransform(transform[0], transform[1], transform[2], transform[3])
        self.data = None
        self.elevation = None
        self.costs = None
        self.df = None
        self.costs_canvas = None
        self.costs_preview = None
        self.name = name
        self.grid = None
        if model:
            self.project_id = model.project_id
        else:
            self.project_id = 0

        # self.model = model
        self.dffinder = None
        self.mdf = None
        self.feature = None

    @property
    def model(self) -> models.Level:
        # print(self.name, self.project_id)
        # levels = models.Level.objects.filter(name = self.name)
        # print(levels)
        return models.Level.objects.filter(name = self.name, project_id = self.project_id).first()

    def create_dffinder(self):
        # self.mdf = np.power(self.df, 0.2)
        # self.mdf = np.max(self.mdf[1]) - self.mdf
        # self.mdf = np.power(self.mdf, 4.0)
        # self.mdf = self.mdf.astype(np.float32)
        elevation = self.elevation.astype(np.float32)
        print(self.model)
        self.dffinder = dffinding.DFFinder(self.costs, elevation, self.feature, self.get_recorded_path(), self.model.distance_field_threshold)
    
    def generate_distance_fields(self):
        if type(self.df) == type(None) :
            self.df = np.zeros(self.elevation.shape, dtype=np.float32)
        if self.df.shape != self.elevation.shape:
            self.df = np.zeros(self.elevation.shape, dtype=np.float32)
        # scorecard.bruteforce_generate_distancefields(self.elevation, self.df, tuple((*self.transform.min_point,)), tuple((*self.transform.max_point,)))
        scorecard.approximate_distance_fields(self.elevation, self.df, 0.5)
        self.model.has_distance_field = True
        self.model.save()
        

    def classify_costs(self, elevation_based : bool = False, elevation_alpha_power : float = 0.05, elevation_alpha_beta : float = 1.5, elevation_alpha_beta_power : float = 7.0, just_paths = False, use_df = False):
        if not just_paths:
            scorecard.Scorecard.score(self.model, self.transform, self.data, self.elevation, self.df, self.costs, elevation_based, elevation_alpha_power, elevation_alpha_beta, elevation_alpha_beta_power, use_df=use_df)
        if isinstance(self.model.recorded_paths, list):
            for idx, path in enumerate(self.model.recorded_paths):
                level = path['layer']
                array_to_use = self.elevation
                if use_df:
                    array_to_use = self.df
                min_elevation = np.min(array_to_use[level])
                max_elevation = np.max(array_to_use[level])
                x = path['x']
                y = path['y']
                p = 1
                if idx > 0:
                    p = math.floor(math.pow(scorecard.distance(x,y,1, self.model.recorded_paths[idx-1]['x'], self.model.recorded_paths[idx-1]['y'], 1), 1))
                    if p > 10:
                        p = 2
                # print("Using radius:", p)
                
                for ox in range(-p, p):
                    for oy in range(-p, p):
                        ix = x + ox
                        iy = y + oy
                        self.elevation[level][ix][iy] = path['elevation']
                        if ix < self.elevation[level].shape[0] and iy < self.elevation[level].shape[1]:
                            if array_to_use[level][x][y] > 0:
                                elevation_alpha = scorecard.remap(array_to_use[level][ix][iy], min_elevation, max_elevation, 0.0, 1.0)
                                elevation_alpha = math.pow(math.pow(elevation_alpha, elevation_alpha_power)*elevation_alpha_beta, elevation_alpha_beta_power)*10
                                elevation_value = scorecard.remap(elevation_alpha, 0.0, 1.0, min_elevation, max_elevation)
                                self.costs[level][ix][iy] = 1 + max(elevation_value*0.25, 1.0)
                            
            scorecard.Scorecard.score(self.model, self.transform, self.data, self.elevation, self.df, self.costs, elevation_based, elevation_alpha_power, elevation_alpha_beta, elevation_alpha_beta_power, True, use_df=use_df)


    def get_best_navmesh_level(self, position : Tuple[int, int, float]):
        d = math.inf
        l = 1
        for level in range(self.elevation.shape[0]):
            if position[0] >= 0 and position[0] < self.elevation.shape[1] and position[1] >= 0 and position[1] < self.elevation.shape[2]:
                c = abs(self.elevation[level][position[0]][position[1]] - position[2])
                if c < d:
                    d = c
                    l = level
        if l > 9:
            l = min(9, l)
        return l


    # Call this after initialising Level
    def pre_process_data(self, layers : int = 10):
        _width = self.transform.width+1
        _height = self.transform.height + 1

        print("Creating arrays with size: ", _width, _height)
        self.data = np.zeros((layers, _width, _height), dtype=np.float32)
        self.elevation = np.zeros((layers, _width, _height), dtype=np.float32)
        self.costs = np.zeros((layers, _width, _height), dtype=np.float32)
        self.costs_canvas = np.zeros((layers, _width, _height), dtype=np.float32)

        self.df = np.zeros((layers, _width, _height), dtype=np.float32)
        self.feature = np.zeros((layers, _width, _height), dtype=np.int32)

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

    def set_df_at(self, value : float, index_x : int, index_y : int, level : int = 0):
        try:
            self.df[level][index_y-1][index_x-1] = value
        except Exception as e:
            print(level, index_x-1, index_y-1)
            raise(e)
    
    def set_feature_at(self, value : int, index_x : int, index_y : int, level : int = 0):
        try:
            self.feature[level][index_y-1][index_x-1] = value
        except Exception as e:
            print(level, index_x-1, index_y-1)
            raise(e)

    def post_process_data(self):
        # scorecard.Scorecard.score(self.data, self.costs)
        if not self.grid:
            # self.grid = Grid(matrix = self.costs)
            self.transform.width = self.costs.shape[0]
            self.transform.height = self.costs.shape[1]

    

    def get_valid_point_in_radius(self, arr : np.ndarray, x: int, y : int, radius: float = 10.0, level = 0) -> list:
        return [x, y]
        if type(self.mdf)!=type(None) and self.dffinder:
           
            pos = (int32(x), int32(y), int32(level))
            pos =  self.dffinder.ensure_point_valid(pos)
            # max_tries = 900
            # tries = 0
            # while (not self.dffinder._is_within_threshold(pos)) and tries < max_tries:
            #     for i in range(-5, 5):
            #         for j in range(-5, 5):
            #             pos = (int32(pos[0]+i), int32(pos[1]+j), pos[2])
            #     tries += 1
            return (pos[0], pos[1])

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
            #   if found:
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

    def find_path_safe(self, start: tuple, end: tuple, level : int = 0, target_level : int = 0, only_land = False) -> list:
        path = []
        used_dffinder = False
        if self.dffinder:
            
            path = self.dffinder.find((int32(start[0]), int32(start[1]), int32(level)), (int32(end[0]), int32(end[1]), int32(target_level)), only_land)
            used_dffinder = True
            if len(path) > 0:
                p = np.array(path)
                p_simplified_coords_idx = simplify_coords_idx(p, 100)
                p_simplified = p[p_simplified_coords_idx]
                path = list(p_simplified)
            
        if not self.dffinder:
            path = pyastar.astar_path(self.costs[level], start, end, allow_diagonal=True)
            used_dffinder = False
        # print("Finding at: ", (int32(start[0]), int32(start[1]), int32(level)), (int32(end[0]), int32(end[1]), int32(target_level)), used_dffinder)
        return path, used_dffinder

    def get_cost_to(self, start : Tuple[int, int, int], end : Tuple[int, int, int]):
        start_v = self.get_valid_point_in_radius(self.costs, start[0], start[1], 5)
        end_v = self.get_valid_point_in_radius(self.costs, end[0], end[1], 5)

        start = (start_v[0], start_v[1], start[2])
        end = (end_v[0], end_v[1], end[2])
        if self.dffinder:
            return self.dffinder.get_direction_cost(start, end, 1)
        return 0.0

    def astar(self, start : tuple, end : tuple, safe=True , all : bool = False, elevation : Union[float, None] = None, target_elevation : Union[float, None] = 0.0, recurse_depth : int = 0,
        only_land : bool = False, use_base_level: bool = False, return_raw_path: bool = False, use_single_level = False, single_level = 0) -> list:
        # print("running astar  ", start, end)
        # print("size of data: ", self.data.shape)
        #path, cost = route_through_arrays(self.costs, start, end, fully_connected=False, geometric=True) # astar(self.data, start, end)
        #if not safe:
        #    path = self.find_path(start, self.get_valid_point_in_radius(self.costs, end[0], end[1], 10))
        #else:
        # return []
        # print('finding path', start, end)
        if not use_base_level:
            best_level =  self.get_best_navmesh_level((start[0], start[1], elevation))
            target_best_level = self.get_best_navmesh_level((end[0], end[1], target_elevation))
        else:
            best_level = 0
            target_best_level = 0
        if use_single_level:
            best_level = single_level
            target_best_level = single_level
        # print('best navmesh level: ', best_level)
        if (start[0] > 0 and start[0] < self.costs.shape[1] and start[1] > 0 and start[1] < self.costs.shape[2]
            and end[0] > 0 and end[0] < self.costs.shape[1] and end[1] > 0 and end[1] < self.costs.shape[2]):
                # print("Start elevation at {} - {}:".format(str(start), elevation), self.elevation[best_level][start[0]][start[1]])
                # print(start, end)
                path, udffinder = self.find_path_safe(
                    self.get_valid_point_in_radius(self.costs, start[0], start[1], 5), 
                    self.get_valid_point_in_radius(self.costs, end[0], end[1], 5), best_level, target_best_level, only_land)
        else:
            print("Outside of map", start, end)
            return []
        #print('got path')
        #path = astar(self.costs, start, end)
        # path_and_cost = [(p[0], p[1], self.costs[p[0]][p[1]] ) for p in path]
        if return_raw_path:
            return list(path)
        world_paths = []
        if type(path) != type(None):
            for idx, p in enumerate(path):
                # self.costs_preview[p[0]][p[1]] = 0.5
                wxy = self.transform.transform_to_world((int32(p[1]), int32(p[0])))
                if self.dffinder and udffinder:
                    # print(p, udffinder)\
                    wxy = self.transform.transform_to_world((int32(p[1]), int32(p[0])))
                    y = float(self.elevation[p[2]][p[0]][p[1]])
                    if self.feature[p[2]][p[0]][p[1]] == 1:
                        y = float(self.elevation[0][p[0]][p[1]])
                    world_paths.append({
                        "x": wxy[0],
                        "y": y,
                        "z": wxy[1]
                    })
                else:
                    world_paths.append({
                        "x": wxy[0],
                        "y": float(self.elevation[best_level][p[0]][p[1]]+1),
                        "z": wxy[1]
                    })
                # if not self.dffinder:
                # if idx > 1 and idx < len(path)-1:
                #     if abs(world_paths[idx]['y']-world_paths[idx-1]['y']) > 5.0 and recurse_depth < 1:
                #         print("finding depth path")
                #         world_paths += self.astar(path[idx+2], end, elevation=elevation, recurse_depth = recurse_depth+1)
                #         break
                # 
                # if idx > 50:
                #     break
            if self.dffinder:
                # Reverse paths
                world_paths.reverse()
            if not self.dffinder:
                for idx, wp in enumerate(world_paths):
                    if idx > 1 and idx+4 < len(path)-1:
                        if abs(world_paths[idx+4]['y']-world_paths[idx-1]['y']) > 5.0 and recurse_depth < 1:
                            print("finding depth path")
                            world_paths[idx:] = self.astar(path[idx+4], end, elevation=elevation, recurse_depth = recurse_depth+1)
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
    
    def get_recorded_path(self): # -> List[Tuple[int, int, int]]:
        path = List()
        if len(self.model.recorded_paths) == 0:
            path.append((-1, -1, -1))
        for p in self.model.recorded_paths:
            path.append((
                p['x'], p['y'], p['layer'] 
            ))
        return path

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
                    # self.elevation = np.load(f)
                    scorecard.flip_scorecard(np.load(f), self.elevation)
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
    