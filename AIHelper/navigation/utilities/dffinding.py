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
    ('graph', types.DictType(*kv_ty)),
    ('path', types.ListType(ptv)),
    ('nodes', types.ListType(ptvp)),
    ('keys', types.ListType(ptv)),
    ('closed_nodes', types.ListType(ptvp)),
    ('graph_lookup', types.ListType(gl)),
    ('values', float32[:, :, :]),
    ('elevation', float32[:, :, :]),
    
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
    def __init__(self, values : np.ndarray, elevation : np.ndarray, threshold : float32 = 3.0):
        self.graph = typed.Dict.empty(*kv_ty)
        self.path = typed.List.empty_list(ptv)
        self.nodes = typed.List.empty_list(ptvp)
        self.keys = typed.List.empty_list(ptv)
        self.closed_nodes = typed.List.empty_list(ptvp)
        self.graph_lookup = typed.List.empty_list(gl)
        self.values = values
        self.elevation = elevation
        # for level in range(values.shape[0]):
        #     for x in range(values.shape[1]):
        #         for y in range(values.shape[2]):
        #             value = float32(values[level][x][y])
        #             if value < threshold:
        #                 self.graph[(x, y, level)] = (value, float32(elevation[level][x][y]), int32(x), int32(y), int32(level))
        #                 key = (int32(x), int32(y), int32(level))
        #                 self.keys.append(key)
        #                 self.graph_lookup.append((key, int32(-1)))
    
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
        return key[0] >= 0 and key[0] <= self.elevation.shape[1] \
            and key[1] >= 0 and key[1] <= self.elevation.shape[2] \
                and key[2] >= 0 and key[2] <= self.elevation.shape[0]

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
        if self._ingrid(key):
            return self.values[key[2]][key[0]][key[1]] < float32(32.0) and self.values[key[2]][key[0]][key[1]] > float32(0.0) #and key[2] > 0
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

    def find(self, start : Tuple[int, int, int], end : Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        queue = PriorityQueue()
        start = self.ensure_point_valid((int32(start[0]), int32(start[1]), int32(start[2])))
        end = self.ensure_point_valid((int32(end[0]), int32(end[1]), int32(end[2])))

        null_ptv = (int32(-1), int32(-1), int32(-1))

        self.path = typed.List.empty_list(ptv)
        
        
        came_from = typed.Dict.empty(*pdt)
        came_from[start] = null_ptv
        costs_so_far = typed.Dict.empty(*cmt)
        costs_so_far[start] = float32(math.inf)
        
        queue.put(start, float32(0))
        current = start
        just_started=  True
        i = int32(0)
        while (not queue.empty()) and i < 5000:
            current = queue.get()

            #if i % 10 == 0:
            #    print('['+str(i)+'] - Distance to goal: '+str(int(self._hfdistance(current, end))))

            if current == end:
                # print("Current is end")
                break
            x = current[0]
            y = current[1]
            level = current[2]
            neighbours = [(int32(x-1), int32(y), int32(level)), (int32(x+1), int32(y), int32(level)), 
                (int32(x), int32(y-1), int32(level)), (int32(x), int32(y+1), int32(level)), (int32(x), int32(y), int32(level-1)),
                    (int32(x), int32(y), int32(level+1))]

            for next in neighbours:
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
                    priority = float32(self._hfdistance(next, end)) #float32(self._hdistance(self.graph[next], self.graph[end]))
                    queue.put(next, priority)
                    came_from[next] = current
            i += 1
        
        return self.build_path(came_from, start, end)

    def find_costs(self, start : Tuple[int, int, int], end : Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        queue = PriorityQueue()
        start = self.ensure_point_valid((int32(start[0]), int32(start[1]), int32(start[2])))
        end = self.ensure_point_valid((int32(end[0]), int32(end[1]), int32(end[2])))

        null_ptv = (int32(-1), int32(-1), int32(-1))

        self.path = typed.List.empty_list(ptv)
        
        
        came_from = typed.Dict.empty(*pdt)
        came_from[start] = null_ptv
        costs_so_far = typed.Dict.empty(*cmt)
        costs_so_far[start] = float32(math.inf)
        
        queue.put(start, float32(0))
        current = start
        just_started=  True
        i = int32(0)
        while (not queue.empty()) and i < 5000:
            current = queue.get()

            #if i % 10 == 0:
            #    print('['+str(i)+'] - Distance to goal: '+str(int(self._hfdistance(current, end))))

            if current == end:
                # print("Current is end")
                break
            x = current[0]
            y = current[1]
            level = current[2]
            neighbours = [(int32(x-1), int32(y), int32(level)), (int32(x+1), int32(y), int32(level)), 
                (int32(x), int32(y-1), int32(level)), (int32(x), int32(y+1), int32(level)), (int32(x), int32(y), int32(level-1)),
                    (int32(x), int32(y), int32(level+1))]

            for next in neighbours:
                if not self._ingrid(next): continue
                if not self._is_within_threshold(next): continue
                # print("Sampling neighbours")
                if costs_so_far[current] < math.inf:
                    new_cost = costs_so_far[current] + self._cost(current, next, end)
                else:
                    new_cost = self._cost(current, next ,end)
                 #self._hdistance(self.graph[current], self.graph[next])
                if next not in costs_so_far or new_cost < costs_so_far[next]:
                    costs_so_far[next] = new_cost
                    priority = float32(self._hfdistance(next, end)) #float32(self._hdistance(self.graph[next], self.graph[end]))
                    queue.put(next, priority)
                    came_from[next] = current
            i += 1
        
        return self.build_costs(came_from, costs_so_far, start, end)

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
                    #print(k)
            tries += 1
        return k

    def build_path(self, came_from :types.DictType(types.Tuple((int32, int32, int32)), types.Tuple((int32, int32, int32))), start : types.Tuple((int32, int32, int32)), end : types.Tuple((int32, int32, int32))):
        current = end
        path = typed.List.empty_list(ptv)
        if current not in came_from:
            # print("Could not find path", came_from)
            return path
        while current != start:
            path.append(current)
            current = came_from[current]
        path.append(start)
        return path

    def build_costs(self, came_from :types.DictType(types.Tuple((int32, int32, int32)), types.Tuple((int32, int32, int32))), costs_so_far : types.DictType(*cmt), start : types.Tuple((int32, int32, int32)), end : types.Tuple((int32, int32, int32))):
        current = end
        cost = float32(0.0)
        # print(costs_so_far)
        if current not in came_from:
            # print("Could not find path", came_from)
            return cost
        while current != start:
            if costs_so_far[current] < float32(math.inf):
                cost += self.values[current[2]][current[0]][current[1]]
            current = came_from[current]
        
        return cost


if __name__ == "__main__":
    with open("./models/Project/BF3 Bots 0.0.4/Level/MP_017/df.npy", "rb") as f:
        df = np.load(f)
    with open("./models/Project/BF3 Bots 0.0.4/Level/MP_017/elevation.npy", "rb") as f:
        elevation = np.load(f)


    df = np.power(df, 0.2)
    df = np.max(df[1]) - df
    df = np.power(df, 4.0)
    df = df.astype(np.float32)
    elevation = elevation.astype(np.float32)

    finder = DFFinder(df, elevation, 32)
    #print(finder.graph)
    # (461, 947, 1) (518, 1004, 1)
    start = (99, 342, 0)
    # start = (1145, 407, 1)
    end = (57, 407, 0)
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