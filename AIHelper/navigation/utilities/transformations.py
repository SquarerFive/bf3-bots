# safe remap: https://stackoverflow.com/questions/929103/convert-a-number-range-to-another-range-maintaining-ratio

import math
from numba import njit
#def remap( x, oMin, oMax, nMin, nMax ):
#
#    #range check
#    if oMin == oMax:
#        print ("Warning: Zero input range")
#        return None
#
#    if nMin == nMax:
#        print ("Warning: Zero output range")
#        return None
#
#    #check reversed input range
#    reverseInput = False
#    oldMin = min( oMin, oMax )
#    oldMax = max( oMin, oMax )
#    if not oldMin == oMin:
#        reverseInput = True
#
#    #check reversed output range
#    reverseOutput = False   
#    newMin = min( nMin, nMax )
#    newMax = max( nMin, nMax )
#    if not newMin == nMin :
#        reverseOutput = True
#
#    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
#    if reverseInput:
#        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)
#
#    result = portion + newMin
#    if reverseOutput:
#        result = newMax - portion
#
#    return result

@njit()
def remap(value, old_min, old_max, new_min, new_max):
    old_range = (old_max - old_min)
    new_range = (new_max - new_min)
    return (((value - old_min)*new_range)/old_range)+new_min

def normalize(x, min_value, max_value):
    return abs((x - min_value) / (max_value - min_value))

@njit()
def c_transform_to_world(xy : tuple, width : int, height: int, min_point: tuple, max_point: tuple):
    nx = remap(xy[0], 0, width, min_point[0], max_point[0])
    ny = remap(xy[1], 0, height, min_point[1], max_point[1])

    # wx = remap(nx, 0.0, 1.0, min_point[0], max_point[0])
    # wy = remap(ny, 0.0, 1.0, min_point[1], max_point[1])

    return (nx, ny)

class GridTransform:
    def __init__(self, min_point, max_point, width, height):
        self.min_point = min_point
        self.max_point = max_point
        self.width = width
        self.height = height
    
    def transform_to_world(self, xy : tuple) -> tuple:
        
        nx = remap(xy[0], 0, self.width, self.min_point[0], self.max_point[0])
        ny = remap(xy[1], 0, self.height, self.min_point[1], self.max_point[1])
        #nx = 1.0 - nx
        # ny = 1.0 - ny
        # first, 0 to width = min_point.x to max_point.x 
        wx = remap(nx, 0, 1.0, self.min_point[0], self.max_point[0])
        # 0 to height, min_point.y to max_point.y
        wy = remap(ny, 0, 1.0, self.min_point[1], self.max_point[1])
        
        return (nx, ny)
        
    def transform_to_grid(self, wxy : tuple) -> tuple:
        #print(wxy)
        #print(self.min_point ,self.max_point)
        #print("transform to grid")
        #x = normalize(wxy[0], self.min_point[0], self.max_point[0])
        #y = normalize(wxy[1], self.min_point[1], self.max_point[1])
        x = remap(wxy[0], self.min_point[0], self.max_point[0], 0, self.width)
        y = remap(wxy[1], self.min_point[1], self.max_point[1], 0, self.height)
        #y = self.height - y
        #print('grid @ ', x,y)
        #x = x * (abs(self.width - 0)) + 0
        #y = y * (abs(self.height - 0)) + 0
        
        return (
            int(y),int(x))

    def lerp(self, x : float, y: float, alpha : float) -> float:
        return x + alpha * (y-x)

    def contrast(self, value : float , contrast : float) -> float:
        g = value
        v = self.lerp(0-contrast, contrast+1, g)
        return v
    
    def as_dict(self) -> dict:
        return {
            "min_point": [*self.min_point],
            "max_point": [*self.max_point],
            "width": self.width,
            "height": self.height
        }

    
def from_dict(data : dict) -> GridTransform:
    transformation : GridTransform = GridTransform(
        data['min_point'], data['max_point'], data['width'], data['height']
    )
    return transformation

@njit()
def transform_to_world(xy : tuple, min_point: tuple, max_point : tuple, width: float, height: float) -> tuple:
    nx = remap(xy[0], 0, width, 0.0, 1.0)
    ny = remap(xy[1], 0, height, 0.0, 1.0)
    # nx = 1.0 - nx
    # ny = 1.0 - ny
    # first, 0 to width = min_point.x to max_point.x 
    wx = remap(nx, 0, 1.0, min_point[0], max_point[0])
    # 0 to height, min_point.y to max_point.y
    wy = remap(ny, 0, 1.0, min_point[1], max_point[1])
    return (wy, wx)