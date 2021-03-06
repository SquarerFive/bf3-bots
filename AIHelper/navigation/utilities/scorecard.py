import numpy as np
from numba import prange, njit, jit
import shapely
from shapely.geometry import shape, GeometryCollection, Point
from . import transformations
from .. import models
from shapely.vectorized import contains
import math

from .transformations import remap, c_transform_to_world

from . import jumpflooding

@njit(parallel = True)
def bruteforce_generate_distancefields(elevation_arr : np.ndarray, distance_field_array : np.ndarray, min_point : tuple, max_point : tuple):
    sample_radius = 32.0
    threshold = 0.6
    for level in prange(elevation_arr.shape[0]):
        for x in prange(elevation_arr.shape[1]):
            for y in prange(elevation_arr.shape[2]):
                min_distance = math.inf
                wx, wy = c_transform_to_world((y, x), elevation_arr.shape[1], elevation_arr.shape[2], min_point, max_point)
                for nx in range(-sample_radius, sample_radius):
                    for ny in range(-sample_radius, sample_radius):
                        cx = x + nx
                        cy = y + ny
                        cwx, cwy = c_transform_to_world((cy, cx), elevation_arr.shape[1], elevation_arr.shape[2], min_point, max_point)
                        if cx > 0 and cx < elevation_arr.shape[1] and cy > 0 and cy < elevation_arr.shape[2]:
                            d = math.sqrt(math.pow((cwx - wx), 2)+ math.pow((cwy - wy), 2))*100
                            if d < min_distance and (elevation_arr[level][cx][cy] - elevation_arr[level][x][y]) > threshold:
                                min_distance = d
                if min_distance < math.inf:
                    distance_field_array[level][x][y] = min_distance
                else:
                    distance_field_array[level][x][y] = 0.0

def approximate_distance_fields(elevation_array : np.ndarray, distance_field_array : np.ndarray, seed_value : np.float32):
    for level in range(elevation_array.shape[0]):
        texture = np.abs(np.gradient(elevation_array[level], axis=0))
        jf_tx = np.zeros((*elevation_array[level].shape, 3), dtype=np.float32)
        jumpflooding.initial(texture, jf_tx, seed_value)
        jumpflooding.run_jfd(
            texture, jf_tx, distance_field_array[level], seed_value, 4
        )
        jumpflooding.run_jfd(
            texture, jf_tx, distance_field_array[level], seed_value, 8
        )
        jumpflooding.run_jfd(
            texture, jf_tx, distance_field_array[level], seed_value, 16
        )
        jumpflooding.run_jfd(
            texture, jf_tx, distance_field_array[level], seed_value, 32
        )
        print(np.max(distance_field_array[level]))
        print("Done level", level)
        distance_field_array[level] = np.power(distance_field_array[level], 0.8)
        # distance_field_array[level] = 

@njit(parallel=True)
def score_fast(
    input_arr : np.ndarray, 
    elevation_arr : np.ndarray, 
    target : np.ndarray, 
    level : int,
    roads_mask : np.ndarray, 
    structures_mask : np.ndarray, 
    elevation_based : bool = False,
    elevation_alpha_power : float = 0.05, 
    elevation_alpha_beta : float = 1.5, 
    elevation_alpha_beta_power : float = 7.0,
    df_based : bool = False
    ):
    min_elevation = elevation_arr[level].min()
    max_elevation = elevation_arr[level].max()
    for x in prange(input_arr.shape[1]):
        for y in prange(input_arr.shape[2]):
            if (roads_mask[x][y] or structures_mask[x][y]) and not df_based:
                if roads_mask[x][y]:
                    elevation_alpha = remap(elevation_arr[level][x][y], min_elevation, max_elevation, 0.0, 1.0)
                    elevation_alpha = math.pow(math.pow(elevation_alpha, elevation_alpha_power)*elevation_alpha_beta, elevation_alpha_beta_power)*10
                    elevation_value = remap(elevation_alpha, 0.0, 1.0, min_elevation, max_elevation)
                    if elevation_arr[level][x][y] > 0.0:
                        # print(target)
                        target[level][x][y] = 1 + max(elevation_value*0.25, 1.0)
                    else:
                        target[level][x][y] = math.inf
                if structures_mask[x][y]:
                    elevation_alpha = remap(elevation_arr[level][x][y], min_elevation, max_elevation, 0.0, 1.0)
                    elevation_alpha = math.pow(math.pow(elevation_alpha, elevation_alpha_power)*elevation_alpha_beta, elevation_alpha_beta_power)*10
                    elevation_value = remap(elevation_alpha, 0.0, 1.0, min_elevation, max_elevation)
                    if elevation_arr[level][x][y] > 0.0:
                        target[level][x][y] = 1 + max(elevation_value*2.25, 1.0)
                    else:
                        target[level][x][y] = math.inf
            
            else:
                if level == 0 and not (elevation_based or df_based):
                    if input_arr[level][x][y] == 0.0:# or roads_mask[x][y]:
                        target[level][x][y] = 1.0 + (elevation_arr[level][x][y])
                    if input_arr[level][x][y] == 256:
                        target[level][x][y] = 256
                    if input_arr[level][x][y] == 500: # else:
                        target[level][x][y] = 500
                    if input_arr[level][x][y] == 700:
                        elevation_alpha = remap(elevation_arr[level][x][y], min_elevation, max_elevation, 0.0, 1.0)
                        elevation_alpha = math.pow(math.pow(elevation_alpha, elevation_alpha_power)*elevation_alpha_beta, elevation_alpha_beta_power)
                        elevation_value = remap(elevation_alpha, 0.0, 1.0, min_elevation, max_elevation)
                        target[level][x][y] = 700 + elevation_value 
                elif (level > 0 or elevation_based) and not df_based:
                    if min_elevation > 0.0 and max_elevation > 0.0:
                        elevation_alpha = remap(elevation_arr[level][x][y], min_elevation, max_elevation, 0.0, 1.0)
                        elevation_alpha = math.pow(math.pow(elevation_alpha, elevation_alpha_power)*elevation_alpha_beta, elevation_alpha_beta_power)*10
                        elevation_value = remap(elevation_alpha, 0.0, 1.0, min_elevation, max_elevation)
                        if elevation_arr[level][x][y] > 0.0:
                            target[level][x][y] = 1 + max(elevation_value, 1.0)
                        else:
                            target[level][x][y] = math.inf
                    else:
                        target[level][x][y] = math.inf
                    
                elif df_based:
                    target[level][x][y] = max(1.0, 1.0 + math.pow((max_elevation - elevation_arr[level][x][y]), 4.0))

@njit(parallel=True)
def score_fast_masks(
    input_arr : np.ndarray, 
    elevation_arr : np.ndarray, 
    target : np.ndarray, 
    level : int,
    roads_mask : np.ndarray, 
    structures_mask : np.ndarray, 
    elevation_based : bool = False,
    elevation_alpha_power : float = 0.05, 
    elevation_alpha_beta : float = 1.5, 
    elevation_alpha_beta_power : float = 7.0,
    df_based : bool = False
    ):
    min_elevation = elevation_arr[level].min()
    max_elevation = elevation_arr[level].max()
    for x in prange(input_arr.shape[1]):
        for y in prange(input_arr.shape[2]):
            if (roads_mask[x][y] or structures_mask[x][y]) and not df_based:
                if roads_mask[x][y]:
                    elevation_alpha = remap(elevation_arr[level][x][y], min_elevation, max_elevation, 0.0, 1.0)
                    elevation_alpha = math.pow(math.pow(elevation_alpha, elevation_alpha_power)*elevation_alpha_beta, elevation_alpha_beta_power)*10
                    elevation_value = remap(elevation_alpha, 0.0, 1.0, min_elevation, max_elevation)
                    if elevation_arr[level][x][y] > 0.0:
                        target[level][x][y] = 1 + max(elevation_value*0.25, 1.0)
                    else:
                        target[level][x][y] = math.inf
                if structures_mask[x][y]:
                    elevation_alpha = remap(elevation_arr[level][x][y], min_elevation, max_elevation, 0.0, 1.0)
                    elevation_alpha = math.pow(math.pow(elevation_alpha, elevation_alpha_power)*elevation_alpha_beta, elevation_alpha_beta_power)*10
                    elevation_value = remap(elevation_alpha, 0.0, 1.0, min_elevation, max_elevation)
                    if elevation_arr[level][x][y] > 0.0:
                        target[level][x][y] = 1 + max(elevation_value*2.25, 1.0)
                    else:
                        target[level][x][y] = math.inf
            if df_based and structures_mask[x][y]:
                target[level][x][y] = target[level][x][y]*2

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

# Copy A into B
@njit(parallel = True)
def copy_into(a : np.ndarray, b : np.ndarray):
    for z in prange(a.shape[0]):
        for x in prange(a.shape[1]):
            for y in prange(a.shape[2]):
                b[z][x][y] = a[z][x][y]

# Replace array value with value where mask=threshold
@njit(parallel=False, debug=True)
def mask_replace_with(a : np.ndarray, mask: np.ndarray, threshold: int = 1, value: float = 0.0):
    for x in prange(a.shape[0]):
        for y in prange(a.shape[1]):
            if mask[x][y] == threshold:
                a[x][y] = value

def get_world_array(transform : transformations.GridTransform, input_arr : np.ndarray) -> tuple:
    x_arr = np.zeros((input_arr.shape[1], input_arr.shape[2]), dtype=np.float32)
    y_arr = np.zeros((input_arr.shape[1], input_arr.shape[2]), dtype=np.float32)
    get_world_array_fast(x_arr, y_arr, (*transform.min_point,), (*transform.max_point,), transform.width, transform.height)
    return (x_arr, y_arr)

def score(model: models.Level, transform : transformations.GridTransform,  input_arr : np.ndarray, elevation_arr : np.ndarray, distance_field_arr : np.ndarray, target : np.ndarray, layer : int = 0, elevation_based : bool = False,
    elevation_alpha_power : float = 0.05, elevation_alpha_beta : float = 1.5, elevation_alpha_beta_power : float = 7.0, masks_only = False, use_df = False):
    roads_valid = False
    structures_valid = False
    if model.roads:
        if isinstance(model.roads, list):
            if 'features' in list(model.roads[layer].keys()):
                print("Valid road for layer: ", layer)
                roads_valid = True
    if roads_valid:
        roads_data = model.roads[layer]['features']
        roads = GeometryCollection([shape(feature['geometry']).buffer(0.0) for feature in roads_data]).buffer(0.0)
        x_arr, y_arr = get_world_array(transform, input_arr)
        road_mask = contains(roads, x_arr, y_arr)
    else:
        road_mask = np.full((input_arr.shape[1], input_arr.shape[2]), False, dtype=bool)
    if model.structures:
        if isinstance(model.structures, list):
            if 'features' in list(model.structures[layer].keys()):
                structures_valid = True
    if structures_valid:
        structures_data = model.structures[layer]['features']
        structures = GeometryCollection([shape(feature['geometry']).buffer(0.0) for feature in structures_data]).buffer(0.0)
        x_arr, y_arr = get_world_array(transform, input_arr)
        structures_mask = contains(structures, x_arr, y_arr)
    else:
        structures_mask = np.full((input_arr.shape[1], input_arr.shape[2]), False, dtype=bool)

    print(f"""
    "useDF: {use_df}
    elevationAlphaPower: {elevation_alpha_power}
    elevationAlphaBeta: {elevation_alpha_beta}
    elevationAlphaBetaPower: {elevation_alpha_beta_power} """)
    try:
        arr_to_use = elevation_arr
        if use_df:
            print("Copying array into input")
            arr_to_use = distance_field_arr.copy()
            arr_to_use = np.power(arr_to_use, 0.2)
            arr_to_use = np.max(arr_to_use[1]) - arr_to_use
            arr_to_use = np.power(arr_to_use, 4.0)
            copy_into(arr_to_use, target)
            
        if not (masks_only and use_df):
            
            score_fast(input_arr, arr_to_use, target, layer,  road_mask, structures_mask, elevation_based, elevation_alpha_power, elevation_alpha_beta, elevation_alpha_beta_power, df_based=use_df)
        else:
            score_fast_masks(input_arr, arr_to_use, target, layer,  road_mask, structures_mask, elevation_based, elevation_alpha_power, elevation_alpha_beta, elevation_alpha_beta_power, df_based=use_df)
    except Exception as e:
        print("Failed to score, ", str(e), target)
        raise(e)
    structures_mask = None
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

@njit
def distance(x1 : float, y1 : float, z1 : float,  x2 : float, y2 : float, z2 : float ) -> float:
    return math.sqrt(
        math.pow(x2-x1, 2)+
        math.pow(y2-y1, 2)+
        math.pow(z2-z1, 2)
    )

# score our grid, 

class Scorecard:
    @staticmethod
    def score(model : models.Level, transform : transformations.GridTransform, input_arr:np.ndarray, elevation_arr : np.ndarray, distance_field_arr : np.ndarray, target:np.ndarray, elevation_based = False, 
        elevation_alpha_power : float = 0.05, elevation_alpha_beta : float = 1.5, elevation_alpha_beta_power : float = 7.0, masks_only : bool = False, use_df : bool = False) -> None:
        # score_fast(input_arr, elevation_arr, target)
        for level in range(input_arr.shape[0]):
            score(model, transform, input_arr, elevation_arr, distance_field_arr, target, level, elevation_based, elevation_alpha_power, elevation_alpha_beta, elevation_alpha_beta_power, masks_only, use_df)
        # score(model, transform, input_arr, elevation_arr, target, 1, elevation_based, elevation_alpha_power, elevation_alpha_beta, elevation_alpha_beta_power)
        # score(model, transform, input_arr, elevation_arr, target, 2, elevation_based, elevation_alpha_power, elevation_alpha_beta, elevation_alpha_beta_power)
        # score(model, transform, input_arr, elevation_arr, target, 3, elevation_based, elevation_alpha_power, elevation_alpha_beta, elevation_alpha_beta_power)
        # score(model, transform, input_arr, elevation_arr, target, 4, elevation_based, elevation_alpha_power, elevation_alpha_beta, elevation_alpha_beta_power)
    
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