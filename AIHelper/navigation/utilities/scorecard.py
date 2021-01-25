import numpy as np
from numba import prange, njit

@njit
def score_fast(input_arr:np.ndarray, elevation_arr : np.ndarray, target:np.ndarray):
    for x in prange(input_arr.shape[0]):
        for y in prange(input_arr.shape[1]):
            if input_arr[x][y] == 0.0:
                target[x][y] = 1.0 + elevation_arr[x][y]
            elif input_arr[x][y] == 256:
                target[x][y] = np.inf
            else:
                target[x][y] = np.inf

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
    def score(input_arr:np.ndarray, elevation_arr : np.ndarray, target:np.ndarray) -> None:
        score_fast(input_arr, elevation_arr, target)
    
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