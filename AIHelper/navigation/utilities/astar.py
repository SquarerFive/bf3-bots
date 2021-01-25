import multiprocessing as mp
import pyastar
import numpy as np

from . import scorecard

def fast_astar(queue : mp.Queue, array: np.ndarray, start : tuple, end: tuple):
    with open("./exports/costs31-12-2020.npy", "rb") as f:
        arr = np.load(f)
        new_arr = np.zeros(arr.shape)
        scorecard.flip_scorecard(arr, new_arr)
        arr = new_arr
        arr = arr.astype(np.float32)
        queue.put(
            pyastar.astar_path(arr, start, end, allow_diagonal=True)
        )

def astar(array : np.ndarray, start: tuple, end :tuple):
    try:
        mp.set_start_method('spawn')
    except:
        pass

    queue = mp.Queue()
    process = mp.Process(target = fast_astar, args=(queue, array, start, end))
    process.start()
    path = queue.get()
    process.join()
    return path