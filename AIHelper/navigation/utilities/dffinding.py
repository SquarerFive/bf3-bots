# SquarerFive - 2021, Experimental distance field finder.

from typing import Tuple
import numpy as np
import math

class DFFinder:
    def __init__(self, values : np.ndarray, elevation : np.ndarray, threshold : float = 3.0):
        self.graph = {}
        for level in range(values.shape[0]):
            for x in range(values.shape[1]):
                for y in range(values.shape[2]):
                    if values[level][x][y] > threshold:
                        self.graph[(x, y, level)] = [values[level][x][y], elevation[level][x][y], x, y, level]
    
    def _hdistance(self, n1, n2) -> float:
        return math.sqrt(
            math.pow(n2[2]-n1[2], 2)+
            math.pow(n2[3]-n1[3], 2)+
            math.pow(math.pow(n2[0]-n1[0], 2), 0.2)+
            math.pow(n2[1]-n1[1], 2)
        )

    def _isatdestination(self, n1, destination) -> bool:
        return (n1[2] == destination[2] and n1[3] == destination[3] and n1[4] == destination[4]) or self._hdistance(n1, destination) < 1.0

    def find(self, start : Tuple[int, int, int], end : Tuple[int, int, int]):
        path = []
        current_node = self.graph[start]
        end_node = self.graph[end]
        min_node = None
        min_distance = self._hdistance(current_node, self.graph[end])
        while not self._isatdestination(current_node, end_node):
            min_distance = self._hdistance(current_node, end_node)
            for x in range(current_node[2]-2, current_node[2]+3):
                for y in range(current_node[3]-2, current_node[3]+3):
                    for l in range(current_node[4]-1, current_node[4]+2):
                        n = self.graph.get((x, y, l))
                        if n:
                            d = self._hdistance(n, end_node)
                            if d < min_distance:
                                min_distance = d
                                min_node = n
                                # path.append((min_node[2], min_node[3], min_node[4]))
            if min_node:
                current_node = min_node
                path.append((current_node[2], current_node[3], current_node[4]))
        print("Found path!!!", path, [(p[0], p[1]) for p in path])

if __name__ == "__main__":
    with open("AIHelper/models/Project/BF3 Bots 0.0.4/Level/MP_Subway/df.npy", "rb") as f:
        df = np.load(f)
    with open("AIHelper/models/Project/BF3 Bots 0.0.4/Level/MP_Subway/elevation.npy", "rb") as f:
        elevation = np.load(f)

    finder = DFFinder(df, elevation, 0.1)
    print(finder.graph)
    start = (253, 574, 1)
    end = (326, 582, 1)
    finder.find(start, end)