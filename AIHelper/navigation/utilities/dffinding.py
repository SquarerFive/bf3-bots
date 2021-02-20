# SquarerFive - 2021, Experimental distance field finder.

from typing import List, Tuple
import numba
import numpy as np
import math
from numba.experimental import jitclass
from numba import float32, int32
from numba import types, typed

kv_ty = (types.Tuple((types.int32, types.int32, types.int32)), types.Tuple((types.float32, types.float32, types.int32, types.int32, types.int32)))
gl = (types.Tuple((types.Tuple((int32, int32, int32)), int32)))
# [((0,0,0), 0)]
pt = types.List(types.Tuple((int32, int32, int32)))
ptv = types.Tuple((int32, int32, int32))
ptvp = types.Tuple((types.Tuple((int32, int32, int32)), int32))
spec = [
    ('graph', types.DictType(*kv_ty)),
    ('path', types.ListType(ptv)),
    ('nodes', types.ListType(ptvp)),
    ('keys', types.ListType(ptv)),
    ('closed_nodes', types.ListType(ptvp)),
    ('graph_lookup', types.ListType(gl))
]

# @jitclass(spec)
class DFFinder:
    def __init__(self, values : np.ndarray, elevation : np.ndarray, threshold : float32 = 3.0):
        self.graph = typed.Dict.empty(*kv_ty)
        self.path = typed.List.empty_list(ptv)
        self.nodes = typed.List.empty_list(ptvp)
        self.keys = typed.List.empty_list(ptv)
        self.closed_nodes = typed.List.empty_list(ptvp)
        self.graph_lookup = typed.List.empty_list(gl)
        for level in range(values.shape[0]):
            for x in range(values.shape[1]):
                for y in range(values.shape[2]):
                    value = float32(values[level][x][y])
                    if value < threshold:
                        self.graph[(x, y, level)] = (value, float32(elevation[level][x][y]), int32(x), int32(y), int32(level))
                        key = (int32(x), int32(y), int32(level))
                        self.keys.append(key)
                        self.graph_lookup.append((key, int32(-1)))
    
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
                    min_node = open_nodes[i]
                i = 0
        return sorted_nodes
            


    def _isatdestination(self, n1, destination) -> bool:
       #  print(n1, destination)
        return (n1[2] == destination[2] and n1[3] == destination[3] and n1[4] == destination[4]) or self._hdistance(n1, destination) < 10.0

    def _getindex(self, node, lookup):
        return int32(lookup.index(node))

    def _addtolookup(self, node, lookup):
        found = False
        fidx = 0
        for idx, n in enumerate(lookup):
            if n[0] == node[0]:
                found = True
                fidx = idx
                break
        if found == True:
            self.graph_lookup[fidx] = node
        else:
            self.graph_lookup.append(node)
        
        return node
    
    def node_eq(self, n1, n2):
        if n1 == None:
            return False
        if n2 == None:
            return False
        return n1 == n2

    def find(self, start : Tuple[int, int, int], end : Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        self.path = typed.List.empty_list(ptv)
        self.nodes : list = typed.List.empty_list(ptvp)
        parent_graph_lookup = self.graph_lookup.copy()
        self.closed_nodes = typed.List.empty_list(ptvp)
        
        current_node = ((int32(start[0]), int32(start[1]), int32(start[2])), int32(-1))
        start_node = ((int32(start[0]), int32(start[1]), int32(start[2])), int32(-1))
        goal_node = ((int32(end[0]), int32(end[1]), int32(end[2])), int32(-1))
        self.nodes.append(current_node)
        while len(self.nodes) > 0:
            self.nodes = self._sort_node(self.nodes, end)
            
            current_node = self.nodes.pop(0)
            self.closed_nodes.append(current_node)
            if self._isatdestination(self.graph[current_node[0]], self.graph[goal_node[0]]):
                while not (self.node_eq(current_node, goal_node) and current_node != None):
                    # print(current_node)
                    self.path.append(current_node[0])
                    current_node = (parent_graph_lookup[current_node[1]])
                return self.path.reverse()
        
            x = current_node[0][0]
            y = current_node[0][1]
            level = current_node[0][2]
    
            neighbours = [(x-1, y, level), (x+1, y, level), (x, y-1, level), (x, y+1, level), (x, y, level-1), (x, y, level+1)]
    
            for next in neighbours:
                if not self._haskey(next):
                    continue
                neighbour = self._addtolookup((next, self._getindex(current_node, parent_graph_lookup)), parent_graph_lookup)
    
                if neighbour in self.closed_nodes:
                    continue
                
                should_add = True
                for node in self.nodes:
                    if node == neighbour and self._hdistance(self.graph[neighbour[0]], self.graph[goal_node[0]]) >= self._hdistance(self.graph[node[0]], self.graph[goal_node[0]]):
                        should_add = False
                        break
                if should_add:
                    self.nodes.append(neighbour)

            # min_distance = self._hdistance(current_node, end_node)
            # for x in range(current_node[2]-radius, current_node[2]+radius):
            #     for y in range(current_node[3]-radius, current_node[3]+radius):
            #         for l in range(current_node[4]-1, current_node[4]+1):
            #             
            #             key = (int32(x), int32(y), int32(l))
            #             if not self._haskey(key): continue
            #             n = self.graph[key]
            #             if n != None:
            #                 d = self._hdistance(n, end_node)
            #                 if d < min_distance:
            #                     min_distance = d
            #                     min_node = n
            #                     min_key = key
            #                     self.nodes.append((min_node[2], min_node[3], min_node[4]))
            #         if self._haskey(min_key):
            #             current_node = self.graph[min_key]
            #             self.closed_nodes.append(min_key)
            #             print('valid key '+ str(int32(self._hdistance(current_node, end_node))))
            #     # path.append((current_node[2], current_node[3], current_node[4]))
        #print("Done gathering points")
        #min_distance = self._hdistance(self.graph[start], self.graph[end])
        #for node in self.nodes:
        #    n = self.graph[node]
        #    d = self._hdistance(n, end_node)
        #    if d < min_distance:
        #        self.path.append(node)
#
        ##print("Found path!!!", self.path, [(p[0], p[1]) for p in self.path])\
        #return self.path
        return self.path

if __name__ == "__main__":
    with open("./models/Project/BF3 Bots 0.0.4/Level/MP_Subway/df.npy", "rb") as f:
        df = np.load(f)
    with open("./models/Project/BF3 Bots 0.0.4/Level/MP_Subway/elevation.npy", "rb") as f:
        elevation = np.load(f)
    df = np.power(df, 0.2)
    df = np.max(df[1]) - df
    df = np.power(df, 4.5)
    df = df.astype(np.float32)
    finder = DFFinder(df, elevation, 32)
    #print(finder.graph)
    start = (507, 1145, 1)
    # start = (1145, 407, 1)
    end = (652, 1149, 1)
    # print(df[start[2]][start[0]][start[1]])
    print("FINDING PATH....")
    path = finder.find(start, end)
    print(path)
    # print("Found path!!!", [(p[0], p[1]) for p in path])