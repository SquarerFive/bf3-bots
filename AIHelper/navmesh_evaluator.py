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


with open("./models/Project/BF3 Bots 0.0.4/Level/XP1_004/elevation.npy", "rb") as f:
    elevation : numpy.ndarray = numpy.load(f)[0]
    elevation_g = numpy.abs(numpy.gradient(elevation, axis=0))
    # print(elevation_g)
    

with open("./models/Project/BF3 Bots 0.0.4/Level/MP_Subway/data.npy", "rb") as f:
    with open('./models/Project/BF3 Bots 0.0.4/Level/XP1_004/df.npy', 'rb') as fx:
        elevation_arr = numpy.load(fx)[0]
        # elevation_arr = numpy.power(elevation_arr, 0.2)
        # elevation_arr = numpy.max(elevation_arr[1]) - elevation_arr
        # elevation_arr = numpy.power(elevation_arr, 4.0)

    with open('./models/Project/BF3 Bots 0.0.4/Level/XP1_004/costs.npy', 'rb') as fx:
        costs_arr = numpy.load(fx)[0]
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
    # path = pyastar.astar_path(arr, (1100, 924 ),  get_valid_point_in_radius(arr, 1044, 938 ), allow_diagonal=True)

    te = time.time()
    print(te - ts)
    
    # print(path)

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
    path =  [(1199, 2097, 0),(1200, 2097, 0),(1200, 2096, 0),(1201, 2096, 0),(1201, 2095, 0),(1202, 2095, 0),(1202, 2094, 0),(1203, 2094, 0),(1203, 2093, 0),(1203, 2093, 1),(1204, 2093, 1),(1204, 2092, 1),(1205, 2092, 1),(1205, 2091, 1),(1205, 2090, 1),(1206, 2090, 1),(1206, 2089, 1),(1207, 2089, 1),(1207, 2088, 1),(1207, 2087, 1),(1207, 2086, 1),(1207, 2085, 1),(1207, 2084, 1),(1207, 2083, 1),(1207, 2082, 1),(1208, 2082, 1),(1208, 2081, 1),(1209, 2081, 1),(1209, 2080, 1),(1209, 2079, 1),(1210, 2079, 1),(1210, 2078, 1),(1211, 2078, 1),(1211, 2077, 1),(1212, 2077, 1),(1212, 2076, 1),(1212, 2075, 1),(1213, 2075, 1),(1213, 2074, 1),(1213, 2073, 1),(1214, 2073, 1),(1214, 2072, 1),(1215, 2072, 1),(1215, 2071, 1),(1215, 2070, 1),(1216, 2070, 1),(1216, 2069, 1),(1216, 2068, 1),(1216, 2067, 1),(1216, 2066, 1),(1216, 2065, 1),(1216, 2064, 1),(1216, 2063, 1),(1216, 2062, 1),(1216, 2061, 1),(1216, 2060, 1),(1216, 2059, 1),(1216, 2058, 1),(1216, 2057, 1),(1216, 2056, 1),(1216, 2055, 1),(1216, 2054, 1),(1216, 2053, 1),(1216, 2052, 1),(1216, 2051, 1),(1216, 2050, 1),(1216, 2049, 1),(1216, 2048, 1),(1216, 2047, 1),(1216, 2046, 1),(1216, 2045, 1),(1216, 2044, 1),(1216, 2043, 1),(1216, 2042, 1),(1216, 2041, 1),(1216, 2040, 1),(1216, 2039, 1),(1216, 2038, 1),(1216, 2037, 1),(1216, 2036, 1),(1216, 2035, 1),(1216, 2034, 1),(1216, 2033, 1),(1216, 2032, 1),(1216, 2031, 1),(1216, 2030, 1),(1216, 2029, 1),(1216, 2028, 1),(1216, 2027, 1),(1216, 2026, 1),(1216, 2025, 1),(1216, 2024, 1),(1216, 2023, 1),(1216, 2022, 1),(1216, 2021, 1),(1216, 2020, 1),(1216, 2019, 1),(1216, 2018, 1),(1216, 2017, 1),(1216, 2016, 1),(1216, 2015, 1),(1216, 2014, 1),(1216, 2013, 1),(1216, 2012, 1),(1216, 2011, 1),(1216, 2010, 1),(1216, 2009, 1),(1216, 2008, 1),(1216, 2007, 1),(1216, 2006, 1),(1216, 2005, 1),(1216, 2004, 1),(1216, 2003, 1),(1216, 2002, 1),(1216, 2001, 1),(1216, 2000, 1),(1216, 1999, 1),(1216, 1998, 1),(1216, 1997, 1),(1216, 1996, 1),(1216, 1995, 1),(1216, 1994, 1),(1216, 1993, 1),(1216, 1992, 1),(1216, 1991, 1),(1216, 1990, 1),(1216, 1989, 1),(1216, 1988, 1),(1216, 1987, 1),(1216, 1986, 1),(1216, 1985, 1),(1216, 1984, 1),(1216, 1983, 1),(1216, 1982, 1),(1216, 1981, 1),(1216, 1980, 1),(1216, 1979, 1),(1216, 1978, 1),(1216, 1977, 1),(1216, 1976, 1),(1216, 1975, 1),(1216, 1974, 1),(1216, 1973, 1),(1216, 1972, 1),(1216, 1971, 1),(1216, 1970, 1),(1216, 1969, 1),(1216, 1968, 1),(1216, 1967, 1),(1216, 1966, 1),(1216, 1965, 1),(1216, 1964, 1),(1216, 1963, 1),(1216, 1962, 1),(1216, 1961, 1),(1216, 1960, 1),(1216, 1959, 1),(1216, 1958, 1),(1216, 1957, 1),(1216, 1956, 1),(1216, 1955, 1),(1216, 1954, 1),(1216, 1953, 1),(1216, 1952, 1),(1216, 1951, 1),(1216, 1950, 1),(1216, 1949, 1),(1216, 1948, 1),(1216, 1947, 1),(1216, 1946, 1),(1216, 1945, 1),(1216, 1944, 1),(1216, 1943, 1),(1216, 1942, 1),(1216, 1941, 1),(1216, 1940, 1),(1216, 1939, 1),(1216, 1938, 1),(1216, 1937, 1),(1216, 1936, 1),(1216, 1935, 1),(1216, 1934, 1),(1216, 1933, 1),(1216, 1932, 1),(1216, 1931, 1),(1216, 1930, 1),(1216, 1929, 1),(1216, 1928, 1),(1216, 1927, 1),(1216, 1926, 1),(1216, 1925, 1),(1216, 1924, 1),(1216, 1923, 1),(1216, 1922, 1),(1216, 1921, 1),(1216, 1920, 1),(1216, 1919, 1),(1216, 1918, 1),(1216, 1917, 1),(1216, 1916, 1),(1216, 1915, 1),(1216, 1914, 1),(1216, 1913, 1),(1216, 1912, 1),(1216, 1911, 1),(1216, 1910, 1),(1216, 1909, 1),(1216, 1908, 1),(1216, 1907, 1),(1216, 1906, 1),(1216, 1905, 1),(1216, 1904, 1),(1216, 1903, 1),(1216, 1902, 1),(1216, 1901, 1),(1216, 1900, 1),(1216, 1899, 1),(1216, 1898, 1),(1216, 1897, 1),(1216, 1896, 1),(1216, 1895, 1),(1216, 1894, 1),(1216, 1893, 1),(1216, 1892, 1),(1216, 1891, 1),(1216, 1890, 1),(1216, 1889, 1),(1216, 1888, 1),(1216, 1887, 1),(1216, 1886, 1),(1216, 1885, 1),(1216, 1884, 1),(1216, 1883, 1),(1216, 1882, 1),(1216, 1881, 1),(1216, 1880, 1),(1216, 1879, 1),(1216, 1878, 1),(1216, 1877, 1),(1216, 1876, 1),(1216, 1875, 1),(1216, 1874, 1),(1216, 1873, 1),(1216, 1872, 1),(1216, 1871, 1),(1216, 1870, 1),(1216, 1869, 1),(1216, 1868, 1),(1216, 1867, 1),(1216, 1866, 1),(1216, 1865, 1),(1216, 1864, 1),(1216, 1863, 1),(1216, 1862, 1),(1216, 1861, 1),(1216, 1860, 1),(1215, 1860, 1),(1215, 1859, 1),(1215, 1858, 1),(1215, 1857, 1),(1215, 1856, 1),(1215, 1855, 1),(1215, 1854, 1),(1215, 1853, 1),(1215, 1852, 1),(1215, 1851, 1),(1215, 1850, 1),(1215, 1849, 1),(1215, 1848, 1),(1215, 1847, 1),(1215, 1846, 1),(1215, 1845, 1),(1215, 1844, 1),(1215, 1843, 1),(1215, 1842, 1),(1215, 1841, 1),(1215, 1840, 1),(1215, 1839, 1),(1215, 1838, 1),(1215, 1837, 1),(1215, 1836, 1),(1215, 1835, 1),(1215, 1834, 1),(1215, 1833, 1),(1215, 1832, 1),(1215, 1831, 1),(1215, 1830, 1),(1215, 1829, 1),(1215, 1828, 1),(1215, 1827, 1),(1215, 1826, 1),(1215, 1826, 0),(1215, 1825, 0),(1215, 1824, 0),(1215, 1823, 0),(1215, 1822, 0),(1215, 1821, 0),(1215, 1820, 0),(1214, 1820, 0),(1214, 1819, 0),(1214, 1818, 0),(1214, 1817, 0),(1214, 1816, 0),(1214, 1815, 0),(1213, 1815, 0),(1213, 1814, 0),(1213, 1813, 0),(1213, 1812, 0),(1213, 1811, 0),(1213, 1810, 0),(1213, 1809, 0),(1212, 1809, 0),(1212, 1808, 0),(1212, 1807, 0),(1212, 1806, 0),(1212, 1805, 0),(1212, 1804, 0),(1211, 1804, 0),(1211, 1803, 0),(1211, 1802, 0),(1211, 1801, 0),(1211, 1800, 0),(1211, 1799, 0),(1211, 1798, 0),(1210, 1798, 0),(1210, 1797, 0),(1210, 1796, 0),(1210, 1795, 0),(1210, 1794, 0),(1210, 1793, 0),(1210, 1792, 0),(1209, 1792, 0),(1209, 1792, 1),(1208, 1792, 1),(1207, 1792, 1),(1207, 1791, 1),(1207, 1790, 1),(1207, 1789, 1),(1207, 1788, 1),(1207, 1787, 1),(1206, 1787, 1),(1206, 1786, 1),(1206, 1785, 1),(1206, 1784, 1),(1206, 1783, 1),(1206, 1782, 1),(1206, 1781, 1),(1205, 1781, 1),(1205, 1780, 1),(1205, 1779, 1),(1205, 1778, 1),(1205, 1777, 1),(1205, 1776, 1),(1205, 1775, 1),(1205, 1774, 1),(1205, 1773, 1),(1205, 1772, 1),(1205, 1771, 1),(1205, 1770, 1),(1205, 1770, 0),(1205, 1769, 0),(1205, 1768, 0),(1205, 1767, 0),(1205, 1766, 0),(1205, 1765, 0),(1205, 1764, 0),(1204, 1764, 0),(1204, 1763, 0),(1204, 1762, 0),(1204, 1761, 0),(1204, 1760, 0),(1204, 1759, 0),(1203, 1759, 0),(1203, 1758, 0),(1203, 1757, 0),(1203, 1756, 0),(1203, 1755, 0),(1203, 1754, 0),(1203, 1753, 0),(1202, 1753, 0),(1201, 1753, 0),(1200, 1753, 0),(1200, 1753, 1),(1200, 1754, 1),(1199, 1754, 1),(1198, 1754, 1),(1197, 1754, 1),(1196, 1754, 1),(1196, 1754, 2),(1195, 1754, 2),(1195, 1753, 2),(1195, 1753, 1),(1195, 1753, 0),(1195, 1752, 0),(1195, 1751, 0),(1195, 1750, 0),(1195, 1749, 0),(1195, 1748, 0),(1195, 1748, 1),(1195, 1747, 1),(1196, 1747, 1),(1196, 1746, 1),(1196, 1745, 1),(1196, 1744, 1),(1196, 1743, 1),(1196, 1742, 1),(1196, 1741, 1),(1196, 1740, 1),(1196, 1739, 1),(1196, 1738, 1),(1196, 1737, 1),(1196, 1736, 1),(1196, 1735, 1),(1196, 1734, 1),(1196, 1733, 1),(1196, 1732, 1),(1196, 1731, 1),(1196, 1731, 0),(1196, 1730, 0),(1196, 1729, 0),(1196, 1728, 0),(1196, 1727, 0),(1196, 1726, 0),(1196, 1725, 0),(1196, 1724, 0),(1196, 1723, 0),(1196, 1722, 0),(1196, 1721, 0),(1196, 1720, 0),(1196, 1719, 0),(1196, 1718, 0),(1196, 1717, 0),(1196, 1716, 0),(1196, 1715, 0),(1196, 1714, 0),(1196, 1713, 0),(1196, 1712, 0),(1196, 1711, 0),(1196, 1710, 0),(1196, 1709, 0),(1196, 1708, 0),(1196, 1707, 0),(1196, 1706, 0),(1196, 1705, 0),]
    if type(path) != type(None) :
        for p in path:
            wx = remap(p[0], 0, 512, -512, -256)
            wy = remap(p[1], 0, 512, 256, 512)
            costs_arr[p[0]][p[1]] = 50*(p[2]+1)
            print(wx, wy)
    

    print(arr)
    image = Image.fromarray((arr*255).astype(numpy.uint8), mode="L")
    image.save("test.png")
    pyplot.imshow(elevation_arr)
    pyplot.show()