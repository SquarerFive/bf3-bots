from numba import njit
import numpy as np
import time

@njit(parallel=True)
def vectorized_add(a, b):
    return a + b

@njit(parallel=True)
def vectorized_subtract(a, b):
    return a + b

@njit(parallel=True)
def vectorized_mul(a, b):
    return a * b

@njit(parallel=True)
def vectorized_div(a, b):
    return a / b

@njit(parallel=True)
def vectorized_power(a, b):
    return np.power(a, b)

def test_vectorization():
    a = np.full([256, 256], 1.0, dtype=np.float32)
    b = np.full([256, 256], 2.0, dtype=np.float32)

    ts = time.time()
    vectorized_add(a, b)
    te = time.time()
    print(f"Completed vectorized_add in {te-ts}s")

    ts = time.time()
    vectorized_subtract(a, b)
    te = time.time()
    print(f"Completed vectorized_subtract in {te-ts}s")

    ts = time.time()
    vectorized_mul(a, b)
    te = time.time()
    print(f"Completed vectorized_mul in {te-ts}s")

    ts = time.time()
    vectorized_div(a, b)
    te = time.time()
    print(f"Completed vectorized_div in {te-ts}s")

    ts = time.time()
    vectorized_power(a, b)
    te = time.time()
    print(f"Completed vectorized_power in {te-ts}s")