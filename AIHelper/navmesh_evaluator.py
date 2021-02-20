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
    with open("./models/Project/BF3 Bots 0.0.4/Level/XP1_004/elevation.npy", "rb") as f:
        elevation = numpy.load(f)
    with open("./models/Project/BF3 Bots 0.0.4/Level/XP1_004/data.npy", "rb") as f:
        arr = numpy.load(f)
        fix_scores(arr, elevation)
        # new_arr = numpy.zeros(arr.shape)
        # flip_scorecard(arr, new_arr)
        arr = new_arr
        arr = arr.astype(numpy.float32)
        path = pyastar.astar_path(arr, (344, 601),  get_valid_point_in_radius(arr, 353, 631), allow_diagonal=True)


with open("./models/Project/BF3 Bots 0.0.4/Level/MP_Subway/elevation.npy", "rb") as f:
    elevation = numpy.load(f)[0]

with open("./models/Project/BF3 Bots 0.0.4/Level/MP_Subway/data.npy", "rb") as f:
    with open('./models/Project/BF3 Bots 0.0.4/Level/MP_Subway/df.npy', 'rb') as fx:
        elevation_arr = numpy.load(fx)[1]
        elevation_arr = numpy.power(elevation_arr, 0.2)
        elevation_arr = numpy.max(elevation_arr) - elevation_arr
        elevation_arr = numpy.power(elevation_arr, 4.0)

    with open('./models/Project/BF3 Bots 0.0.4/Level/MP_Subway/costs.npy', 'rb') as fx:
        costs_arr = numpy.load(fx)[1]
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
    path = [(518, 1004, 1),(517, 1004, 1),(517, 1005, 1),(516, 1005, 1),(516, 1006, 1),(515, 1006, 1),(515, 1007, 1),(515, 1008, 1),(515, 1009, 1),(515, 1010, 1),(515, 1011, 1),(515, 1012, 1),(515, 1013, 1),(515, 1014, 1),(515, 1015, 1),(515, 1016, 1),(515, 1017, 1),(515, 1018, 1),(515, 1019, 1),(515, 1020, 1),(514, 1020, 1),(513, 1020, 1),(512, 1020, 1),(511, 1020, 1),(510, 1020, 1),(509, 1020, 1),(509, 1021, 1),(509, 1022, 1),(509, 1023, 1),(509, 1024, 1),(509, 1025, 1),(509, 1026, 1),(509, 1027, 1),(509, 1028, 1),(509, 1029, 1),(508, 1029, 1),(507, 1029, 1),(507, 1030, 1),(506, 1030, 1),(506, 1031, 1),(506, 1032, 1),(505, 1032, 1),(504, 1032, 1),(504, 1033, 1),(503, 1033, 1),(503, 1034, 1),(502, 1034, 1),(502, 1035, 1),(502, 1036, 1),(502, 1037, 1),(502, 1038, 1),(502, 1039, 1),(501, 1039, 1),(500, 1039, 1),(500, 1040, 1),(500, 1041, 1),(499, 1041, 1),(498, 1041, 1),(497, 1041, 1),(496, 1041, 1),(495, 1041, 1),(494, 1041, 1),(494, 1040, 1),(494, 1039, 1),(493, 1039, 1),(493, 1038, 1),(493, 1037, 1),(493, 1036, 1),(493, 1035, 1),(493, 1034, 1),(493, 1033, 1),(493, 1032, 1),(492, 1032, 1),(492, 1031, 1),(491, 1031, 1),(491, 1030, 1),(490, 1030, 1),(490, 1029, 1),(489, 1029, 1),(489, 1028, 1),(488, 1028, 1),(488, 1027, 1),(487, 1027, 1),(487, 1026, 1),(486, 1026, 1),(486, 1025, 1),(485, 1025, 1),(485, 1024, 1),(485, 1024, 2),(485, 1023, 2),(485, 1023, 3),(485, 1022, 3),(486, 1022, 3),(487, 1022, 3),(487, 1021, 3),(487, 1020, 3),(487, 1019, 3),(486, 1019, 3),(486, 1018, 3),(485, 1018, 3),(485, 1017, 3),(485, 1017, 2),(486, 1017, 2),(487, 1017, 2),(487, 1016, 2),(487, 1016, 1),(488, 1016, 1),(489, 1016, 1),(490, 1016, 1),(491, 1016, 1),(492, 1016, 1),(493, 1016, 1),(494, 1016, 1),(495, 1016, 1),(495, 1015, 1),(495, 1014, 1),(496, 1014, 1),(496, 1013, 1),(496, 1012, 1),(496, 1011, 1),(496, 1010, 1),(496, 1009, 1),(496, 1008, 1),(496, 1007, 1),(496, 1006, 1),(496, 1005, 1),(496, 1004, 1),(496, 1003, 1),(496, 1002, 1),(496, 1001, 1),(496, 1000, 1),(496, 999, 1),(495, 999, 1),(495, 998, 1),(495, 997, 1),(495, 996, 1),(495, 995, 1),(495, 994, 1),(494, 994, 1),(493, 994, 1),(492, 994, 1),(492, 993, 1),(492, 992, 1),(492, 991, 1),(492, 990, 1),(492, 989, 1),(492, 988, 1),(492, 987, 1),(492, 986, 1),(492, 985, 1),(492, 984, 1),(492, 983, 1),(492, 982, 1),(492, 981, 1),(492, 980, 1),(491, 980, 1),(491, 979, 1),(491, 978, 1),(490, 978, 1),(490, 977, 1),(490, 976, 1),(489, 976, 1),(489, 975, 1),(489, 974, 1),(488, 974, 1),(488, 973, 1),(487, 973, 1),(487, 972, 1),(486, 972, 1),(485, 972, 1),(485, 971, 1),(484, 971, 1),(484, 970, 1),(484, 969, 1),(483, 969, 1),(483, 968, 1),(482, 968, 1),(482, 967, 1),(482, 966, 1),(482, 965, 1),(481, 965, 1),(480, 965, 1),(480, 964, 1),(479, 964, 1),(479, 963, 1),(479, 962, 1),(478, 962, 1),(478, 961, 1),(477, 961, 1),(477, 960, 1),(477, 959, 1),(477, 958, 1),(477, 957, 1),(477, 956, 1),(477, 955, 1),(477, 954, 1),(477, 953, 1),(477, 953, 2),(477, 952, 2),(477, 951, 2),(477, 950, 2),(476, 950, 2),(475, 950, 2),(474, 950, 2),(473, 950, 2),(472, 950, 2),(471, 950, 2),(470, 950, 2),(469, 950, 2),(468, 950, 2),(467, 950, 2),(466, 950, 2),(466, 949, 2),(465, 949, 2),(465, 948, 2),(465, 947, 2),(464, 947, 2),(463, 947, 2),(462, 947, 2),(461, 947, 2),(461, 947, 1),]
    if type(path) != type(None) :
        for p in path:
            elevation_arr[p[0]][p[1]] = 50*(p[2]+1)
    

    print(arr)
    image = Image.fromarray((arr*255).astype(numpy.uint8), mode="L")
    image.save("test.png")
    pyplot.imshow(costs_arr)
    pyplot.show()