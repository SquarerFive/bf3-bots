import numpy 
from PIL import Image
import networkx as nx
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.dijkstra import DijkstraFinder
from pathfinding.finder.best_first import BestFirst
from pathfinding.finder.ida_star import IDAStarFinder
from pathfinding.finder.bi_a_star import BiAStarFinder
from pathfinding.finder.breadth_first import BreadthFirstFinder

from matplotlib import pyplot
from scipy.sparse.csgraph import shortest_path
from numba import njit, jit, prange
import math
# from navigation.utilities.astar import astar

import pyastar
import time
from scipy.ndimage.filters import gaussian_filter
# import cv2

@njit()
def remap(value, old_min, old_max, new_min, new_max):
    old_range = (old_max - old_min)
    new_range = (new_max - new_min)
    return (((value - old_min)*new_range)/old_range)+new_min

@njit
def fix_scores(array, elevation : numpy.ndarray):
    min_elevation = elevation.min()
    max_elevation = elevation.max()

    for x in prange(array.shape[0]):
        for y in prange(array.shape[1]):
            if array[x][y] == 0.0:
                array[x][y] = 1 + ( elevation[x][y])
            if array[x][y] == 500:
                array[x][y] = 500
            if array[x][y] == 700:
                elevation_alpha = remap(elevation[x][y], min_elevation, max_elevation, 0.0, 1.0)
                elevation_alpha = math.pow(math.pow(elevation_alpha, 0.25)*1.5, 4)
                elevation_value = remap(elevation_alpha, 0.0, 1.0, min_elevation, max_elevation)
                array[x][y] = 700 + elevation_value 

@njit
def flip_scorecard(array, new_array):
    for x in prange(array.shape[0]):
        for y in prange(array.shape[1]):
            v = new_array.shape[1]-1
            new_array[y][x] = array[x][y]
    
            

def get_path(predecessors, i, j):
    path = [j]
    k = j
    while predecessors[i, k] != -9999:
        path.append(predecessors[i,k ])
        k = predecessors[i, k]
    return path[::-1]

def get_valid_point_in_radius(arr, x, y, radius: float = 10.0):
    offsets = [(-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1)]
    found = False
    # final
    final_pos = [0,0]
    for g in range(1, int(radius)):
        for offset in offsets:
            i = y+(offset[1]*g)
            j = x+(offset[0]*g)
            if arr[i][j] != 0:
                found = True
                final_pos = [j, i]
                break
        if found:
            break
    return final_pos
    #return (final_pos[1], final_pos[0])

def get_path_to(start, end):
    with open("./models/Project/BF3-Bots-0.0.4/Level/XP1_004/elevation.npy", "rb") as f:
        elevation = numpy.load(f)
    with open("./models/Project/BF3-Bots-0.0.4/Level/XP1_004/data.npy", "rb") as f:
        arr = numpy.load(f)
        fix_scores(arr, elevation)
        # new_arr = numpy.zeros(arr.shape)
        # flip_scorecard(arr, new_arr)
        arr = new_arr
        arr = arr.astype(numpy.float32)
        path = pyastar.astar_path(arr, (344, 601),  get_valid_point_in_radius(arr, 353, 631), allow_diagonal=True)


with open("./models/Project/BF3-Bots-0.0.4/Level/XP1_004/elevation.npy", "rb") as f:
    elevation = numpy.load(f)[0]

with open("./models/Project/BF3-Bots-0.0.4/Level/XP1_004/data.npy", "rb") as f:
    arr = numpy.load(f)[0]
    new_arr = numpy.zeros(arr.shape)
    print(new_arr.shape, arr.shape)
    fix_scores(arr, elevation)
    # flip_scorecard(arr, new_arr)
    # arr = new_arr
    # print(arr.transpose())
    
    arr = arr.astype(numpy.float32)
    #arr = gaussian_filter(arr, sigma=1.0).astype(numpy.int32)
    print("finding path")
    # 703 828
    #print(arr[703][828])
    print(arr[828][704])
    #print(arr)
    ts = time.time()
    #path = pyastar.astar_path(arr, (749, 814),  get_valid_point_in_radius(arr, 700, 757), False)
    #path = pyastar.astar_path(arr, (601, 344),  get_valid_point_in_radius(arr, 632, 353), allow_diagonal=False)
    #path = pyastar.astar_path(arr, (353, 659),  get_valid_point_in_radius(arr, 341, 591), allow_diagonal=True)
    #path = pyastar.astar_path(arr, (684, 397),  get_valid_point_in_radius(arr, 658, 444), allow_diagonal=False)
    # path = pyastar.astar_path(arr, (745, 528),  get_valid_point_in_radius(arr, 848, 596), allow_diagonal=True)
    path = pyastar.astar_path(arr, (1100, 924 ),  get_valid_point_in_radius(arr, 1044, 938 ), allow_diagonal=True)

    te = time.time()
    print(te - ts)
    
    print(path)

    # print(arr[432,585])
    # grid = Grid(matrix=arr)
    # start = grid.node(749, 814) #grid.node(864, 793) #grid.node(688, 855)
    # calc_end = get_valid_point_in_radius(arr, 669, 740)
    # end   = grid.node(*calc_end) #grid.node(864, 700) #grid.node(793, 807)
    # print("Running pathfinder")
    # ts = time.time()
    # finder = AStarFinder(diagonal_movement=DiagonalMovement.always, weight=1.0)
    # path , runs = finder.find_path(start, end, grid)
    # te = time.time()
    # print("Done", te-ts)
    if type(path) != type(None) :
        for p in path:
            arr[p[0]][p[1]] = 4
    

    print(arr)
    image = Image.fromarray((arr*255).astype(numpy.uint8), mode="L")
    image.save("test.png")
    pyplot.imshow(arr)
    pyplot.show()