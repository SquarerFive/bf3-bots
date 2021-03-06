# SquarerFive - 2021, Experimental distance field finder.

from typing import List, Tuple
import numba
from numba.core.types.containers import DictType
import numpy as np
import math
from numba.experimental import jitclass
from numba import float32, int32
from numba import types, typed
import heapq



kv_ty = (types.Tuple((types.int32, types.int32, types.int32)), types.Tuple((types.float32, types.float32, types.int32, types.int32, types.int32)))
gl = (types.Tuple((types.Tuple((int32, int32, int32)), int32)))
# [((0,0,0), 0)]
pt = types.List(types.Tuple((int32, int32, int32)))
ptv = types.Tuple((int32, int32, int32))
ptvp = types.Tuple((types.Tuple((int32, int32, int32)), int32))

ptp = types.Tuple((float32, ptv))
cmt = (ptv, float32)
pdt = (ptv, ptv)

spec = [
    # ('graph', types.DictType(*kv_ty)),
    # ('path', types.ListType(ptv)),
    # ('nodes', types.ListType(ptvp)),
    # ('keys', types.ListType(ptv)),
    # ('closed_nodes', types.ListType(ptvp)),
    # ('graph_lookup', types.ListType(gl)),
    ('values', float32[:, :, :]),
    ('elevation', float32[:, :, :]),
    ('threshold', float32),
    ('feature', int32[:, :, :]),
    ('recorded_paths', types.ListType(ptv)),
    ('only_use_static_paths', types.Boolean(''))
    
]
# Ref: https://www.redblobgames.com/pathfinding/a-star/implementation.html
binary_heap_spec = [
    ('elements', types.ListType(ptp))
]
@jitclass(binary_heap_spec)
class PriorityQueue:
    def __init__(self):
        self.elements = typed.List.empty_list(ptp)

    def empty(self) -> bool:
        return not len(self.elements) > 0

    def put(self, item : types.Tuple((int32, int32, int32)), priority : float32):
        elem = list(self.elements)
        heapq.heappush(elem, (priority, item))
        self.elements = typed.List(elem)
    
    def get(self) -> types.Tuple((int32, int32, int32)):
        elem = list(self.elements)
        v = heapq.heappop(elem)[1]
        self.elements = typed.List(elem)
        return v

@jitclass(spec)
class DFFinder:
    def __init__(self, values : np.ndarray, elevation : np.ndarray, feature : np.ndarray, recorded_paths: pt, threshold : float32 = 3.0):
        self.values = values
        self.elevation = elevation
        self.threshold = threshold
        self.feature = feature
        self.recorded_paths = typed.List.empty_list(ptv)
        self.only_use_static_paths = True
        for p in recorded_paths:
            self.recorded_paths.append(
                (
                    int32(p[0]), int32(p[1]), int32(p[2])
                )
            )
    
    def _haskey(self, key) -> bool:
        return key in self.keys

    def _hdistance(self, n1, n2) -> float32:
        # print(n1, n2)
        return math.sqrt(
            math.pow(n2[2]-n1[2], 2)+
            math.pow(n2[3]-n1[3], 2)+
            math.pow(math.pow(n2[0]-n1[0], 2), 1.0)+
            math.pow(n2[1]-n1[1], 2)
        )

    def _ingrid(self, key) -> bool:
        return key[0] >= 0 and key[0] < self.elevation.shape[1] \
            and key[1] >= 0 and key[1] < self.elevation.shape[2] \
                and key[2] >= 0 and key[2] < self.elevation.shape[0]

    def _inrpath(self, key) -> bool:
        for p in self.recorded_paths:
            d = math.sqrt(math.pow(p[0]-key[0],2)+ math.pow(p[1]-key[1], 2)+ math.pow(self._get_elevation(p)-self._get_elevation(key), 2))
            if d < 6:
                return True, p
        return False, key

    def _sort_node(self, in_nodes : List[Tuple[Tuple[int32, int32, int32], int32]], goal : Tuple[int32, int32, int32]):
        sorted_nodes = typed.List.empty_list(ptvp)
        open_nodes = in_nodes.copy()
        min_ = self._hdistance(self.graph[in_nodes[0][0]], self.graph[goal])
        min_node = in_nodes[0]
        i = 0
        while len(open_nodes) > 0:
            v = self._hdistance(self.graph[open_nodes[i][0]], self.graph[goal])
            if v < min_:
                min_ = v
                min_node = open_nodes[i]
            i += 1

            if i == len(open_nodes):
                sorted_nodes.append(min_node)
                open_nodes.remove(min_node)
                if len(open_nodes) > 0:
                    min_ = v
                    min_node = open_nodes[0]
                i = 0
        return sorted_nodes
            


    def _isatdestination(self, n1, destination) -> bool:
       #  print(n1, destination)
        return (n1[2] == destination[2] and n1[3] == destination[3] and n1[4] == destination[4]) or self._hdistance(n1, destination) < 10.0

    def _getindex(self, node, lookup):
        for index, n in enumerate(lookup):
            if n[0] == node[0]:
                return index
        return -1

    def _get_value(self, key):
        return self.values[key[2]][key[0]][key[1]]

    def _get_elevation(self, key):
        return self.elevation[key[2]][key[0]][key[1]]

    def _is_within_threshold(self, key):
       # if key in self.recorded_paths:
       #     return True
        if self._ingrid(key):
            if self.feature[key[2]][key[0]][key[1]] == 1:
                if key[2] == 0:
                    return self.values[key[2]][key[0]][key[1]] < float32(self.threshold)
                else:
                    return False
            else:
                return self.values[key[2]][key[0]][key[1]] < float32(self.threshold)# and self.values[key[2]][key[0]][key[1]] > float32(0.0) #and key[2] > 0
        return False

    def _hfdistance(self, key1, key2):
        return math.sqrt(
            math.pow((self._get_value(key2)-self._get_value(key1)), 2)+
            
            math.pow((key2[0]- key1[0]), 2)+
            math.pow((key2[1]- key1[1]), 2)+
            math.pow(self._get_elevation(key2)-self._get_elevation(key1), 4)
        )
    
    def _cost(self, key1, key2, key3):
        return math.pow(abs((self._get_elevation(key3)-((self._get_elevation(key2)+self._get_elevation(key1))/2))), 2)+abs(
            self._get_value(key2)-self._get_value(key1)
        )#+abs(self._get_elevation(key2)-self._get_elevation(key1))


    def _addtolookup(self, node, lookup):
        found = False
        fidx = 0
        for idx, n in enumerate(lookup):
            if n[0] == node[0]:
                found = True
                fidx = idx
                break
        if found == True:
            lookup[fidx] = node
        else:
            lookup.append(node)
        
        return node
    
    def node_eq(self, n1, n2):
        if n1 == None:
            return False
        if n2 == None:
            return False
        return n1 == n2

    def nodes_getmin(self, nodes, goal):
        min_distance = self._hdistance(self.graph[nodes[0][0]], self.graph[goal[0]])
        min_index = 0
        for index, node in enumerate(nodes):
            d = self._hdistance(self.graph[node[0]], self.graph[goal[0]])
            if d < min_distance:
                min_distance = d
                min_index=  index
        return nodes.pop(min_index)

    def _findrnearest(self, key : Tuple[int32, int32, int32]):
        index = 0
        nearest_distance: float32 = float32(math.inf)
        nearest_point = key
        for idx, p in enumerate(self.recorded_paths):
            d = math.sqrt(math.pow(p[0]-key[0],2)+ math.pow(p[1]-key[1], 2)+ math.pow(self._get_elevation(p)-self._get_elevation(key), 2))
            if d < nearest_distance:
                nearest_distance = d
                index = idx
                nearest_point = p
        return nearest_point, index

    def find(self, start : Tuple[int, int, int], end : Tuple[int, int, int], only_land : bool = False) -> List[Tuple[int, int, int]]:
        queue = PriorityQueue()
        # print("Finding valid points")
        #start = (int32(start[0]), int32(start[1]), int32(start[2]))
        start =  self.ensure_point_valid((int32(start[0]), int32(start[1]), int32(start[2])))
        # end =  (int32(end[0]), int32(end[1]), int32(end[2]))
        end = self.ensure_point_valid  ((int32(end[0]), int32(end[1]), int32(end[2])))
        path = typed.List.empty_list(ptv)
        if not self._is_within_threshold(start) or not self._ingrid(start) or not self._is_within_threshold(end) or not self._ingrid(end):
            start = self.ensure_point_valid((int32(start[0]), int32(start[1]), int32(start[2])))
            end = self.ensure_point_valid  ((int32(end[0]), int32(end[1]), int32(end[2])))
            print("Not in grid", start, end, self._get_value(start), self._get_value(end), self._ingrid(start), self._is_within_threshold(start))
            return path
        null_ptv = (int32(-1), int32(-1), int32(-1))

        # self.path = typed.List.empty_list(ptv)
        
        
        came_from = typed.Dict.empty(*pdt)
        
        costs_so_far = typed.Dict.empty(*cmt)
        
        
        
        current = start
        current_index = 0
        just_started=  True
        if self.only_use_static_paths:
            current, current_index = self._findrnearest(current)
            current = (int32(current[0]), int32(current[1]), int32(current[2]))
            start = current

            end, _ = self._findrnearest(end)
            end = (int32(end[0]), int32(end[1]), int32(end[2]))
            queue.put(current, float32(0))
            came_from[current] = null_ptv
            costs_so_far[current] = float32(math.inf)
        else:
            queue.put(start, float32(0))
            came_from[start] = null_ptv
            costs_so_far[start] = float32(math.inf)

        i = int32(0)
        while (not queue.empty()) and i < 1000:
            current = queue.get()

            # if i % 10 == 0:
            #     print('['+str(i)+'] - Distance to goal: '+str(int(self._hfdistance(current, end))))

            if current == end:
                #print("Current is end")
                break
            x = current[0]
            y = current[1]
            level = current[2]
            

            if not self.only_use_static_paths:
                neighbours = [(int32(x-1), int32(y), int32(level)), (int32(x+1), int32(y), int32(level)), 
                    (int32(x), int32(y-1), int32(level)), (int32(x), int32(y+1), int32(level)), (int32(x), int32(y), int32(level-1)),
                        (int32(x), int32(y), int32(level+1))]

                for next in neighbours:
                    if only_land:
                        if self.feature[next[2]][next[0]][next[1]] == 1:
                            continue
                    if not self._ingrid(next): continue
                    if not self._is_within_threshold(next): continue
                    in_path, next = self._inrpath(next)
                    # print("Sampling neighbours")
                    if costs_so_far[current] < float32(math.inf):
                        new_cost = costs_so_far[current] + self._cost(current, next, end)
                    else:
                        new_cost = self._cost(current, next, end)
                     #self._hdistance(self.graph[current], self.graph[next])
                    # if next in self.recorded_paths:
                    #     print("Recorded path")
                    if (next not in costs_so_far or new_cost < costs_so_far[next]):

                        costs_so_far[next] = new_cost
                        priority = float32(self._hfdistance(next, end))#float32(self._hdistance(self.graph[next], self.graph[end]))
                        #if next in self.recorded_paths:
                        #    priority = float32(priority * 0.5)
                        queue.put(next, priority)
                        came_from[next] = current
                
            else:
                current_index = self._findrnearest(current)[1]
                #neighbours = [-len(self.recorded_paths), len(self.recorded_paths)]
                for next_offset_index in range(-len(self.recorded_paths), len(self.recorded_paths)):
                    next_index = current_index + next_offset_index
                    if next_index == current_index: continue
                    if not (next_index >= 0 and next_index < len(self.recorded_paths)): continue
                    next = self.recorded_paths[next_index]
                    next = (int32(next[0]), int32(next[1]), int32(next[2]))
                    d = math.sqrt(math.pow(next[0]-current[0], 2)+math.pow(next[1]-current[1], 2)+math.pow(self._get_elevation(next)-self._get_elevation(current), 4))
                    if costs_so_far[current] < float32(math.inf):
                        new_cost = costs_so_far[current] + self._cost(current, next, end)+d
                    else:
                        new_cost = self._cost(current, next, end)+d
                    
                    if (next not in costs_so_far or new_cost < costs_so_far[next]) and d < 10:
                        costs_so_far[next] = new_cost
                        priority = float32(self._hfdistance(next, end)+d)
                        # print(next)
                        queue.put(next, priority)
                        came_from[next] = current
            # i += 1

        # print("Done after: "+str(i))
        return self.build_path(came_from, start, end, current)

    def find_costs(self, start : Tuple[int, int, int], end : Tuple[int, int, int], only_land : bool = False) -> List[Tuple[int, int, int]]:
        queue = PriorityQueue()
        # print("Finding valid points")
        #start = (int32(start[0]), int32(start[1]), int32(start[2]))
        start =  self.ensure_point_valid((int32(start[0]), int32(start[1]), int32(start[2])))
        # end =  (int32(end[0]), int32(end[1]), int32(end[2]))
        end = self.ensure_point_valid  ((int32(end[0]), int32(end[1]), int32(end[2])))
        path = typed.List.empty_list(ptv)
        if not self._is_within_threshold(start) or not self._ingrid(start) or not self._is_within_threshold(end) or not self._ingrid(end):
            start = self.ensure_point_valid((int32(start[0]), int32(start[1]), int32(start[2])))
            end = self.ensure_point_valid  ((int32(end[0]), int32(end[1]), int32(end[2])))
            print("Not in grid", start, end, self._get_value(start), self._get_value(end), self._ingrid(start), self._is_within_threshold(start))
            return path
        null_ptv = (int32(-1), int32(-1), int32(-1))

        # self.path = typed.List.empty_list(ptv)
        
        
        came_from = typed.Dict.empty(*pdt)
        came_from[start] = null_ptv
        costs_so_far = typed.Dict.empty(*cmt)
        costs_so_far[start] = float32(math.inf)
        
        queue.put(start, float32(0))
        current = start
        just_started=  True
        i = int32(0)
        while (not queue.empty()) and i < 1000:
            current = queue.get()

            # if i % 10 == 0:
            #     print('['+str(i)+'] - Distance to goal: '+str(int(self._hfdistance(current, end))))

            if current == end:
                #print("Current is end")
                break
            x = current[0]
            y = current[1]
            level = current[2]
            neighbours = [(int32(x-1), int32(y), int32(level)), (int32(x+1), int32(y), int32(level)), 
                (int32(x), int32(y-1), int32(level)), (int32(x), int32(y+1), int32(level)), (int32(x), int32(y), int32(level-1)),
                    (int32(x), int32(y), int32(level+1))]

            for next in neighbours:
                if only_land:
                    if self.feature[next[2]][next[0]][next[1]] == 1:
                        continue
                if not self._ingrid(next): continue
                if not self._is_within_threshold(next): continue
                # print("Sampling neighbours")
                if costs_so_far[current] < float32(math.inf):
                    new_cost = costs_so_far[current] + self._cost(current, next, end)
                else:
                    new_cost = self._cost(current, next, end)
                 #self._hdistance(self.graph[current], self.graph[next])
                if next not in costs_so_far or new_cost < costs_so_far[next]:
                    costs_so_far[next] = new_cost
                    priority = float32(self._hfdistance(next, end))#float32(self._hdistance(self.graph[next], self.graph[end]))
                    queue.put(next, priority)
                    came_from[next] = current
            i += 1
        # print("Done after: "+str(i))
        
        return self.build_costs(came_from, costs_so_far, start, end, current)

    def _mag(self, x : int32, y : int32):
        return math.floor(math.sqrt((x*x)+ (y*y)))

    def _sub(self, a: Tuple[int32, int32, int32], b: Tuple[int32, int32, int32]):
        return (
            a[0]-b[0],
            a[1]-b[1],
            a[2]-b[2]
        )

    def get_direction_cost(self, start: Tuple[int32, int32, int32], end: Tuple[int32, int32, int32], max_length: int32 = 5):
        
        start = (int32(start[0]), int32(start[1]), int32(start[2]))
        end = (int32(end[0]), int32(end[1]), int32(end[2]))
        d = self._sub(end, start)
        m = self._mag(d[0], d[1])
        if m == 0: return 0.0
        nx = int32(math.floor(d[0]/m))
        ny = int32(math.floor(d[1]/m))

        p = [start[0], start[1]]
        cost: float32 = 0.0
        for i in range(0, max_length):
            cost += self.values[start[2]][p[0]][p[1]]
            p[0] += nx*i
            p[1] += ny*i
        return cost

    def ensure_point_valid(self, point):
        k = point
        max_tries = 900
        tries = 0
        while (not self._is_within_threshold(k)) and tries < max_tries:
            for x in range(-25, 25):
                for y in range(-25, 25):
                    if self._ingrid((int32(k[0]+x), int32(k[1]+y), int32(k[2]))) and self._is_within_threshold((int32(k[0]+x), int32(k[1]+y), int32(k[2]))):
                        k = (int32(k[0]+x), int32(k[1]+y), int32(k[2]))
                        
                        break
                    # print(str(tries))
            tries += 1
        print("Found valid point after: " + str(tries) + " tries.")
        return k

    def build_path(self, came_from :types.DictType(types.Tuple((int32, int32, int32)), types.Tuple((int32, int32, int32))), start : types.Tuple((int32, int32, int32)), end : types.Tuple((int32, int32, int32)), defcurrent : types.Tuple((int32,int32,int32))):
        current = end
        path = typed.List.empty_list(ptv)
        # print(came_from)
        if current not in came_from:
            # print("Could not find path", came_from)
            # return path
            current = defcurrent
            
        if start not in came_from:
            print("No start")
            return path
        while current != start:
            path.append(current)
            
            current = came_from[current]
        path.append(start)
        print("Build path")
        return path

    def build_costs(self, came_from :types.DictType(types.Tuple((int32, int32, int32)), types.Tuple((int32, int32, int32))), costs_so_far : types.DictType(*cmt), start : types.Tuple((int32, int32, int32)), end : types.Tuple((int32, int32, int32)), defcurrent : types.Tuple((int32,int32,int32))):
        current = end
        cost = float32(0.0)
        # print(costs_so_far)
        if current not in came_from:
            # print("Could not find path", came_from)
            # return path
            current = defcurrent
        while current != start:
            if costs_so_far[current] < float32(math.inf):
                cost += costs_so_far[current] #self.values[current[2]][current[0]][current[1]]
            current = came_from[current]
        
        return cost


if __name__ == "__main__":
    with open("./models/Project/BF3 Bots 0.0.4/Level/XP1_004/costs.npy", "rb") as f:
        df = np.load(f)
    with open("./models/Project/BF3 Bots 0.0.4/Level/XP1_004/elevation.npy", "rb") as f:
        elevation = np.load(f)
    with open("./models/Project/BF3 Bots 0.0.4/Level/XP1_004/feature.npy", "rb") as f:
        feature = np.load(f)


    # df = np.power(df, 0.2)
    # df = np.max(df[1]) - df
    # df = np.power(df, 4.0)
    # df = df.astype(np.float32)
    elevation = elevation.astype(np.float32)

    finder = DFFinder(df, elevation, feature, 190)
    #print(finder.graph)
    # (461, 947, 1) (518, 1004, 1)
    start = (1119, 1500, 0)
    print(df[start[2]][start[0]][start[1]])
    # start = (1145, 407, 1)
    end = (1164, 2133, 0)
    # print(df[start[2]][start[0]][start[1]])
    print("FINDING PATH....")
    path = finder.find(start, end)
    # path = find(finder, start, end)
    print(path)
    print("Found path!!!", [(p[0], p[1]) for p in path])
    with open('./path.txt', 'w') as f:
        f.write('[')
        for p in path:
            f.write(f'({p[0]}, {p[1]}, {p[2]}),')
        f.write(']')