# SquarerFive 2021 - Approximate a signed distance field using jump flooding.
# I've implemented what I've intepreted from: https://www.comp.nus.edu.sg/~tants/jfa/i3d06.pdf
# This currently runs on the CPU, in parallel. However a CUDA implementation can easily be added.

import numpy as np
from numba import njit, prange
import math

from matplotlib import pyplot

@njit
def clamp(x, min_, max_):
    return max(min(x, max_), min_)

@njit
def distance(p1, p2):
    return math.sqrt(
        math.pow(p1[0] - p2[0], 2) +
        math.pow(p1[1] - p2[1], 2)
    )

class BasicJumpflooding:
    def __init__(self, texture, seed_value : float):
        # self.jf_tx = np.zeros(shape=[*texture.shape, 3], dtype=float)
        self.jf_tx = np.full(shape=[*texture.shape, 3], fill_value=-999.0, dtype=np.float32)
        self.df_tx = np.zeros(shape =texture.shape, dtype = np.float32)
        self.seed_value = seed_value
        self.texture = texture
        self.step_length = 4
    
    #@njit
    def jfd(self, auto_step = True):
        for x in range(0, self.texture.shape[0], self.step_length):
            #if x % self.step_length != 0:   continue
            for y in range(0, self.texture.shape[1], self.step_length):
                #if y % self.step_length != 0: continue
                center_pos = (x,y)
                old_pos = self.jf_tx[center_pos[0]][center_pos[1]]
                current_sample = self.texture[x][y]
                #self.df_tx[x][y] = -1
                for _x in range(-1, (1)+1):
                    for _y in range(-1, (1)+1):
                        if _x == 0 and _y == 0:
                            continue

                        ix = _x * self.step_length
                        iy = _y * self.step_length

                        pos = (
                            clamp(ix + x, 0, self.texture.shape[0]-1), 
                            clamp(iy + y, 0, self.texture.shape[1]-1)
                            )
                        value = self.texture[pos[0]][pos[1]]
                        if value >= self.seed_value:
                            #self.df_tx[_x][_y] = current_sample
                            if distance(center_pos, pos) < distance(center_pos, old_pos):
                                self.jf_tx[x][y][0] = pos[0]
                                self.jf_tx[x][y][1] = pos[1]
                                old_pos = pos[0], pos[1]
                                self.df_tx[x][y] = distance(center_pos, pos) * -1 if \
                                    current_sample >= self.seed_value else 1
                        else:
                            nearest_pos = self.jf_tx[pos[0]][pos[1]][0], self.jf_tx[pos[0]][pos[1]][1]
                            if old_pos[0] == -999.0 and old_pos[1] == -999.0:
                                self.jf_tx[center_pos[0]][center_pos[1]][0] = nearest_pos[0]
                                self.jf_tx[center_pos[0]][center_pos[1]][1] = nearest_pos[1]
                                old_pos = nearest_pos
                                self.df_tx[x][y] = distance(center_pos, nearest_pos) * (-1 if \
                                    current_sample >= self.seed_value else 1)

                            elif distance(center_pos, nearest_pos) < distance(center_pos, old_pos):
                                self.jf_tx[center_pos[0]][center_pos[1]][0] = nearest_pos[0]
                                self.jf_tx[center_pos[0]][center_pos[1]][1] = nearest_pos[1]
                                old_pos = nearest_pos
                                self.df_tx[x][y] = distance(center_pos, nearest_pos) * (-1 if \
                                    current_sample >= self.seed_value else 1)
        self.step_length //= 2
        if self.step_length <= 0:
            return
        if auto_step:                
            
            self.jfd()

# Allocate required resources to run jump flooding
@njit(parallel=True)
def initial(texture, jfd_texture, seed_value = 0.01):
    for x in prange(texture.shape[0]):
        for y in prange(texture.shape[1]):
            value = texture[x][y]
            if value >= seed_value:
                jfd_texture[x][y][0] = x
                jfd_texture[x][y][1] = y

@njit(parallel=True, debug=False)
def jfd(texture, jfd_texture, df_texture, seed_value, step_length):
    # print(texture.shape, jfd_texture.shape, df_texture.shape)
    for x in prange(0, texture.shape[0]):
        if x % step_length != 0:
            continue
        for y in prange(0, texture.shape[1]):
            if y % step_length != 0:
                continue
            center_pos = (x,y)
            old_pos = jfd_texture[center_pos[0]][center_pos[1]]
            current_sample = texture[x][y]
            #self.df_tx[x][y] = -1
            for _x in prange(-1, (1)+1):
                for _y in prange(-1, (1)+1):
                    ix = _x * step_length
                    iy = _y * step_length
                    pos = (
                        clamp(ix + x, 0, texture.shape[0]-1), 
                        clamp(iy + y, 0, texture.shape[1]-1)
                        )
                    
                    
                        
                    value = texture[pos[0]][pos[1]]
                    if value >= seed_value:
                        #self.df_tx[_x][_y] = current_sample
                        if distance(center_pos, pos) < distance(center_pos, old_pos):
                            jfd_texture[x][y][0] = pos[0]
                            jfd_texture[x][y][1] = pos[1]
                            df_texture[x][y] = distance(center_pos, pos) * -1 if \
                                current_sample >= seed_value else 1
                    else:
                        nearest_pos = jfd_texture[pos[0]][pos[1]][0], jfd_texture[pos[0]][pos[1]][1]
                        if old_pos[0] == -999.0 and old_pos[1] == -999.0:
                            jfd_texture[center_pos[0]][center_pos[1]][0] = nearest_pos[0]
                            jfd_texture[center_pos[0]][center_pos[1]][1] = nearest_pos[1]
                            old_pos = jfd_texture[center_pos[0]][center_pos[1]]
                            df_texture[x][y] = distance(center_pos, nearest_pos) * -1 if \
                                current_sample >= seed_value else 1
                        elif distance(center_pos, nearest_pos) < distance(center_pos, old_pos):
                            jfd_texture[center_pos[0]][center_pos[1]][0] = nearest_pos[0]
                            jfd_texture[center_pos[0]][center_pos[1]][1] = nearest_pos[1]
                            old_pos = jfd_texture[center_pos[0]][center_pos[1]]
                            df_texture[x][y] = distance(center_pos, nearest_pos) * (-1 if \
                                current_sample >= seed_value else 1)

# @njit()
def run_jfd(texture, jfd_texture, df_texture, seed_value, step_length):
    step_size=  step_length
    while step_size > 0:
        jfd(texture, jfd_texture, df_texture, seed_value, step_size)
        step_size //= 2

import time

if __name__ == "__main__":
    tex = np.zeros((32,32), dtype=np.float32)
    #tex[0][0] = 1.0
    tex[16][16] = 1.0
    # tex[1][1] = 1.0

    jf_tx = np.zeros((*tex.shape, 3), dtype=np.float32)
    df_tx = np.zeros((*tex.shape,), dtype=np.float32)
    initial(tex, jf_tx, 0.5)
    ts = time.time()
    run_jfd(tex, jf_tx, df_tx, 0.5, 4)
    te = time.time()
    print(te - ts)
    ts = time.time()
    run_jfd(tex, jf_tx, df_tx, 0.5, 4)
    te = time.time()
    print(te - ts)
    # b = BasicJumpflooding(tex, 0.5)
    # ts = time.time()
    # b.jfd()
    # te = time.time()
    # print(te - ts)

    pyplot.imshow(df_tx)
    pyplot.show()