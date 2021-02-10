import numpy as np
from numba import prange, njit, jit
import shapely
from shapely.geometry import shape, GeometryCollection, Point
from . import transformations
from .. import models
from shapely.vectorized import contains
import math

from .transformations import remap

@njit
def score_fast(input_arr:np.ndarray, elevation_arr : np.ndarray, target:np.ndarray, roads_mask : np.ndarray, level : int):
    min_elevation = elevation_arr[level].min()
    max_elevation = elevation_arr[level].max()
    for x in prange(input_arr.shape[1]):
        for y in prange(input_arr.shape[2]):
            if roads_mask[x][y]:
                target[level][x][y] = 1.0 + ((elevation_arr[level][x][y])/2)
            else:
                if level == 0:
                    if input_arr[level][x][y] == 0.0:# or roads_mask[x][y]:
                        target[level][x][y] = 1.0 + (elevation_arr[level][x][y])
                    if input_arr[level][x][y] == 256:
                        target[level][x][y] = 256
                    if input_arr[level][x][y] == 500: # else:
                        target[level][x][y] = 500
                    if input_arr[level][x][y] == 700:
                        elevation_alpha = remap(elevation_arr[level][x][y], min_elevation, max_elevation, 0.0, 1.0)
                        elevation_alpha = math.pow(math.pow(elevation_alpha, 0.125)*1.5, 7)
                        elevation_value = remap(elevation_alpha, 0.0, 1.0, min_elevation, max_elevation)
                        target[level][x][y] = 700 + elevation_value 
                elif level == 1:
                    elevation_alpha = remap(elevation_arr[level][x][y], min_elevation, max_elevation, 0.0, 1.0)
                    elevation_alpha = math.pow(math.pow(elevation_alpha, 0.15)*1.5, 2)
                    elevation_value = remap(elevation_alpha, 0.0, 1.0, min_elevation, max_elevation)
                    target[level][x][y] = elevation_value

@njit(parallel=True)
def get_world_array_fast(x_arr: np.ndarray, y_arr : np.ndarray, min_point : tuple, max_point : tuple, width: float, height: float):
    for x in prange(x_arr.shape[0]):
        for y in prange(x_arr.shape[0]):
            gx, gy = transformations.transform_to_world((x,y), min_point, max_point, width, height)
            # print(gx, gy)
            x_arr[x][y] = gx
            y_arr[x][y] = gy
    # print('finished')
    # print(x_arr)
    # print(y_arr)

def get_world_array(transform : transformations.GridTransform, input_arr : np.ndarray) -> tuple:
    x_arr = np.zeros((input_arr.shape[1], input_arr.shape[2]), dtype=np.float32)
    y_arr = np.zeros((input_arr.shape[1], input_arr.shape[2]), dtype=np.float32)
    get_world_array_fast(x_arr, y_arr, (*transform.min_point,), (*transform.max_point,), transform.width, transform.height)
    return (x_arr, y_arr)

def score(model: models.Level, transform : transformations.GridTransform,  input_arr : np.ndarray, elevation_arr : np.ndarray, target : np.ndarray, layer : int = 0):
    valid = False
    if model.roads:
        if layer in model.roads.keys():
            if 'features' in list(model.roads[layer].keys()):
                valid = True
    if valid:
        roads_data = model.roads[layer]['features']
        roads = GeometryCollection([shape(feature['geometry']).buffer(0.0) for feature in roads_data]).buffer(0.0)
        x_arr, y_arr = get_world_array(transform, input_arr)
        mask = contains(roads, x_arr, y_arr)
    else:
        mask = np.full((input_arr.shape[1], input_arr.shape[2]), False, dtype=bool)
    
    score_fast(input_arr, elevation_arr, target, mask, layer)
    # print('mask', mask)
    # print('roads', roads, Point(-630, -450).intersects(roads))
    # print("scoring")
    # for x in range(input_arr.shape[0]):
    #     for y in range(input_arr.shape[1]):
    #         gx, gy = transform.transform_to_world((x,y))
    #         point = Point(gx, gy)
    #         # print(gx, gy)
    #         # if (point.overlaps(roads)):
    #             # print("point overlaps", gx, gy)
    #         if input_arr[x][y] == 0.0 or point.intersects(roads):
    #             target[x][y] = 1.0 + elevation_arr[x][y]
    #         elif input_arr[x][y] == 256:
    #             target[x][y] = np.inf
    #         else:
    #             target[x][y] = np.inf

@njit
def flip_scorecard(array, new_array):
    for x in prange(array.shape[0]):
        for y in prange(array.shape[1]):
            v = new_array.shape[1]-1
            #new_array[v-y][x] = array[x][y]
            new_array[y][x] = array[x][y]     

# score our grid, 

class Scorecard:
    @staticmethod
    def score(model : models.Level, transform : transformations.GridTransform, input_arr:np.ndarray, elevation_arr : np.ndarray, target:np.ndarray) -> None:
        # score_fast(input_arr, elevation_arr, target)
        score(model, transform, input_arr, elevation_arr, target, 0)
        score(model, transform, input_arr, elevation_arr, target, 1)
        score(model, transform, input_arr, elevation_arr, target, 2)
        score(model, transform, input_arr, elevation_arr, target, 3)
        score(model, transform, input_arr, elevation_arr, target, 4)
    
    @staticmethod
    def flip(input_arr: np.ndarray, target_arr:np.ndarray) -> None:
        flip_scorecard(input_arr, target_arr)

    @staticmethod
    def material(array:np.ndarray, x:int, y:int) -> None:
        pass


def extend(array, start, end):
    for x in range(int(start[0]), int(end[0])):
        for y in range(int(start[1]), int(end[1])):
            array[x][y] = 1.0

if __name__ == "__main__":
    values = np.zeros((2048, 2048))
    steps = 12
    step_size = 2048/steps 
    for i in range(steps):
        for j in range( steps):
            start_x = step_size*i
            end_x = step_size*(i+1)
            start_y = step_size*j
            end_y = step_size*(j+1)
            extend(values, (start_x, start_y), (end_x, end_y))
            print(start_x, end_x, start_y, end_y)
    for x in range(values.shape[0]):
        for y in range(values.shape[1]):
            if values[x][y] != 1.0:
                print("Not 1 at ",x,y)