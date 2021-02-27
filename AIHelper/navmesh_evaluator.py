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
    path =  [(1199, 2097, 0),(1200, 2097, 0),(1200, 2098, 0),(1201, 2098, 0),(1202, 2098, 0),(1202, 2097, 0),(1202, 2096, 0),(1202, 2095, 0),(1202, 2094, 0),(1202, 2093, 0),(1202, 2093, 1),(1202, 2092, 1),(1202, 2091, 1),(1202, 2090, 1),(1202, 2089, 1),(1202, 2088, 1),(1202, 2087, 1),(1202, 2086, 1),(1201, 2086, 1),(1201, 2085, 1),(1201, 2084, 1),(1201, 2083, 1),(1201, 2082, 1),(1201, 2081, 1),(1200, 2081, 1),(1200, 2080, 1),(1199, 2080, 1),(1199, 2079, 1),(1198, 2079, 1),(1197, 2079, 1),(1196, 2079, 1),(1195, 2079, 1),(1194, 2079, 1),(1193, 2079, 1),(1192, 2079, 1),(1191, 2079, 1),(1190, 2079, 1),(1189, 2079, 1),(1188, 2079, 1),(1187, 2079, 1),(1186, 2079, 1),(1185, 2079, 1),(1184, 2079, 1),(1183, 2079, 1),(1182, 2079, 1),(1181, 2079, 1),(1181, 2078, 1),(1181, 2077, 1),(1181, 2077, 0),(1181, 2076, 0),(1181, 2075, 0),(1181, 2074, 0),(1181, 2073, 0),(1181, 2072, 0),(1181, 2071, 0),(1180, 2071, 0),(1180, 2070, 0),(1179, 2070, 0),(1179, 2069, 0),(1179, 2068, 0),(1179, 2067, 0),(1179, 2066, 0),(1179, 2065, 0),(1179, 2064, 0),(1179, 2063, 0),(1179, 2062, 0),(1179, 2061, 0),(1179, 2060, 0),(1179, 2059, 0),(1178, 2059, 0),(1178, 2058, 0),(1178, 2057, 0),(1177, 2057, 0),(1176, 2057, 0),(1175, 2057, 0),(1175, 2056, 0),(1174, 2056, 0),(1173, 2056, 0),(1172, 2056, 0),(1171, 2056, 0),(1170, 2056, 0),(1169, 2056, 0),(1169, 2055, 0),(1168, 2055, 0),(1167, 2055, 0),(1166, 2055, 0),(1166, 2054, 0),(1165, 2054, 0),(1164, 2054, 0),(1164, 2053, 0),(1163, 2053, 0),(1163, 2052, 0),(1162, 2052, 0),(1162, 2051, 0),(1161, 2051, 0),(1161, 2050, 0),(1160, 2050, 0),(1160, 2049, 0),(1160, 2048, 0),(1159, 2048, 0),(1159, 2047, 0),(1159, 2046, 0),(1159, 2045, 0),(1158, 2045, 0),(1158, 2044, 0),(1158, 2043, 0),(1158, 2042, 0),(1158, 2041, 0),(1158, 2040, 0),(1158, 2039, 0),(1158, 2038, 0),(1158, 2037, 0),(1158, 2036, 0),(1158, 2035, 0),(1158, 2034, 0),(1158, 2033, 0),(1159, 2033, 0),(1159, 2032, 0),(1159, 2031, 0),(1160, 2031, 0),(1160, 2030, 0),(1160, 2029, 0),(1160, 2028, 0),(1160, 2027, 0),(1160, 2026, 0),(1160, 2025, 0),(1160, 2024, 0),(1160, 2023, 0),(1160, 2022, 0),(1160, 2021, 0),(1160, 2020, 0),(1160, 2019, 0),(1160, 2018, 0),(1160, 2017, 0),(1160, 2016, 0),(1160, 2015, 0),(1160, 2014, 0),(1160, 2013, 0),(1160, 2012, 0),(1160, 2011, 0),(1160, 2010, 0),(1160, 2009, 0),(1160, 2008, 0),(1160, 2007, 0),(1160, 2006, 0),(1160, 2005, 0),(1160, 2004, 0),(1160, 2003, 0),(1160, 2002, 0),(1160, 2001, 0),(1160, 2000, 0),(1160, 1999, 0),(1160, 1998, 0),(1160, 1997, 0),(1160, 1996, 0),(1160, 1995, 0),(1160, 1994, 0),(1160, 1993, 0),(1160, 1992, 0),(1160, 1991, 0),(1160, 1990, 0),(1160, 1989, 0),(1160, 1988, 0),(1160, 1987, 0),(1160, 1986, 0),(1160, 1985, 0),(1160, 1984, 0),(1160, 1983, 0),(1160, 1982, 0),(1160, 1981, 0),(1160, 1980, 0),(1160, 1979, 0),(1160, 1978, 0),(1160, 1977, 0),(1160, 1976, 0),(1160, 1975, 0),(1160, 1974, 0),(1160, 1973, 0),(1160, 1972, 0),(1160, 1971, 0),(1160, 1970, 0),(1160, 1969, 0),(1160, 1968, 0),(1160, 1967, 0),(1160, 1966, 0),(1160, 1965, 0),(1160, 1964, 0),(1160, 1963, 0),(1159, 1963, 0),(1159, 1962, 0),(1159, 1961, 0),(1158, 1961, 0),(1158, 1960, 0),(1157, 1960, 0),(1157, 1959, 0),(1156, 1959, 0),(1155, 1959, 0),(1155, 1958, 0),(1154, 1958, 0),(1153, 1958, 0),(1152, 1958, 0),(1151, 1958, 0),(1150, 1958, 0),(1149, 1958, 0),(1148, 1958, 0),(1147, 1958, 0),(1147, 1957, 0),(1147, 1956, 0),(1147, 1955, 0),(1147, 1954, 0),(1147, 1953, 0),(1147, 1952, 0),(1147, 1951, 0),(1147, 1950, 0),(1147, 1949, 0),(1147, 1948, 0),(1147, 1947, 0),(1147, 1946, 0),(1147, 1945, 0),(1147, 1944, 0),(1147, 1943, 0),(1147, 1942, 0),(1147, 1941, 0),(1147, 1940, 0),(1147, 1939, 0),(1147, 1938, 0),(1147, 1937, 0),(1147, 1936, 0),(1147, 1935, 0),(1147, 1934, 0),(1147, 1933, 0),(1147, 1932, 0),(1147, 1931, 0),(1147, 1930, 0),(1147, 1929, 0),(1147, 1928, 0),(1147, 1927, 0),(1147, 1926, 0),(1147, 1925, 0),(1147, 1924, 0),(1147, 1923, 0),(1147, 1922, 0),(1147, 1921, 0),(1147, 1920, 0),(1147, 1919, 0),(1147, 1918, 0),(1147, 1917, 0),(1147, 1916, 0),(1147, 1915, 0),(1147, 1914, 0),(1147, 1913, 0),(1147, 1912, 0),(1147, 1911, 0),(1147, 1910, 0),(1147, 1909, 0),(1147, 1908, 0),(1147, 1907, 0),(1147, 1906, 0),(1147, 1906, 1),(1148, 1906, 1),(1148, 1905, 1),(1149, 1905, 1),(1149, 1904, 1),(1149, 1903, 1),(1149, 1903, 0),(1149, 1902, 0),(1149, 1901, 0),(1149, 1900, 0),(1149, 1899, 0),(1149, 1898, 0),(1149, 1897, 0),(1149, 1896, 0),(1149, 1895, 0),(1149, 1894, 0),(1149, 1893, 0),(1149, 1892, 0),(1149, 1891, 0),(1149, 1890, 0),(1149, 1889, 0),(1149, 1888, 0),(1149, 1887, 0),(1149, 1886, 0),(1149, 1885, 0),(1149, 1884, 0),(1149, 1883, 0),(1149, 1882, 0),(1148, 1882, 0),(1148, 1881, 0),(1148, 1880, 0),(1147, 1880, 0),(1147, 1879, 0),(1146, 1879, 0),(1146, 1878, 0),(1145, 1878, 0),(1144, 1878, 0),(1144, 1877, 0),(1144, 1876, 0),(1144, 1875, 0),(1144, 1874, 0),(1144, 1873, 0),(1144, 1872, 0),(1144, 1871, 0),(1144, 1870, 0),(1144, 1869, 0),(1144, 1868, 0),(1144, 1867, 0),(1144, 1866, 0),(1144, 1865, 0),(1144, 1864, 0),(1144, 1863, 0),(1144, 1862, 0),(1144, 1861, 0),(1144, 1860, 0),(1144, 1859, 0),(1144, 1858, 0),(1144, 1857, 0),(1144, 1856, 0),(1144, 1855, 0),(1144, 1854, 0),(1144, 1853, 0),(1144, 1852, 0),(1144, 1851, 0),(1144, 1850, 0),(1144, 1849, 0),(1145, 1849, 0),(1145, 1848, 0),(1146, 1848, 0),(1146, 1847, 0),(1147, 1847, 0),(1147, 1846, 0),(1148, 1846, 0),(1148, 1845, 0),(1149, 1845, 0),(1150, 1845, 0),(1151, 1845, 0),(1152, 1845, 0),(1152, 1844, 0),(1153, 1844, 0),(1153, 1843, 0),(1153, 1842, 0),(1154, 1842, 0),(1154, 1841, 0),(1155, 1841, 0),(1155, 1840, 0),(1155, 1839, 0),(1156, 1839, 0),(1156, 1838, 0),(1156, 1837, 0),(1157, 1837, 0),(1157, 1836, 0),(1157, 1835, 0),(1158, 1835, 0),(1158, 1834, 0),(1159, 1834, 0),(1159, 1833, 0),(1159, 1832, 0),(1160, 1832, 0),(1160, 1831, 0),(1161, 1831, 0),(1161, 1830, 0),(1162, 1830, 0),(1162, 1829, 0),(1163, 1829, 0),(1163, 1828, 0),(1164, 1828, 0),(1164, 1827, 0),(1165, 1827, 0),(1165, 1826, 0),(1166, 1826, 0),(1166, 1825, 0),(1166, 1824, 0),(1167, 1824, 0),(1167, 1823, 0),(1168, 1823, 0),(1168, 1822, 0),(1168, 1821, 0),(1169, 1821, 0),(1169, 1820, 0),(1170, 1820, 0),(1170, 1819, 0),(1171, 1819, 0),(1171, 1818, 0),(1172, 1818, 0),(1172, 1817, 0),(1173, 1817, 0),(1173, 1816, 0),(1174, 1816, 0),(1174, 1815, 0),(1175, 1815, 0),(1176, 1815, 0),(1177, 1815, 0),(1177, 1814, 0),(1177, 1813, 0),(1177, 1812, 0),(1177, 1811, 0),(1177, 1810, 0),(1177, 1809, 0),(1177, 1808, 0),(1177, 1807, 0),(1177, 1806, 0),(1177, 1805, 0),(1177, 1804, 0),(1177, 1803, 0),(1177, 1802, 0),(1177, 1801, 0),(1177, 1800, 0),(1177, 1799, 0),(1177, 1798, 0),(1177, 1797, 0),(1177, 1796, 0),(1177, 1795, 0),(1177, 1794, 0),(1177, 1793, 0),(1177, 1792, 0),(1177, 1791, 0),(1177, 1790, 0),(1177, 1789, 0),(1177, 1788, 0),(1177, 1787, 0),(1177, 1786, 0),(1177, 1785, 0),(1177, 1784, 0),(1177, 1783, 0),(1177, 1782, 0),(1177, 1781, 0),(1177, 1780, 0),(1177, 1779, 0),(1177, 1778, 0),(1177, 1777, 0),(1177, 1776, 0),(1177, 1775, 0),(1177, 1774, 0),(1177, 1773, 0),(1177, 1772, 0),(1177, 1771, 0),(1177, 1770, 0),(1177, 1769, 0),(1177, 1768, 0),(1177, 1767, 0),(1177, 1766, 0),(1177, 1765, 0),(1177, 1764, 0),(1177, 1763, 0),(1177, 1762, 0),(1177, 1761, 0),(1177, 1760, 0),(1177, 1759, 0),(1177, 1758, 0),(1177, 1757, 0),(1177, 1756, 0),(1177, 1755, 0),(1177, 1754, 0),(1177, 1753, 0),(1177, 1752, 0),(1177, 1751, 0),(1177, 1750, 0),(1177, 1749, 0),(1177, 1748, 0),(1177, 1747, 0),(1177, 1746, 0),(1178, 1746, 0),(1178, 1745, 0),(1178, 1744, 0),(1179, 1744, 0),(1179, 1743, 0),(1180, 1743, 0),(1180, 1742, 0),(1181, 1742, 0),(1181, 1741, 0),(1182, 1741, 0),(1183, 1741, 0),(1184, 1741, 0),(1185, 1741, 0),(1186, 1741, 0),(1187, 1741, 0),(1188, 1741, 0),(1189, 1741, 0),(1189, 1740, 0),(1189, 1739, 0),(1189, 1738, 0),(1189, 1737, 0),(1189, 1737, 1),(1190, 1737, 1),(1190, 1736, 1),(1191, 1736, 1),(1191, 1735, 1),(1192, 1735, 1),(1192, 1734, 1),(1193, 1734, 1),(1193, 1733, 1),(1194, 1733, 1),(1194, 1732, 1),(1195, 1732, 1),(1196, 1732, 1),(1196, 1731, 1),(1196, 1730, 1),(1196, 1729, 1),(1196, 1728, 1),(1196, 1727, 1),(1196, 1726, 1),(1196, 1725, 1),(1196, 1725, 0),(1196, 1724, 0),(1196, 1723, 0),(1196, 1722, 0),(1196, 1721, 0),(1196, 1720, 0),(1196, 1719, 0),(1196, 1718, 0),(1196, 1717, 0),(1196, 1716, 0),(1196, 1715, 0),(1196, 1714, 0),(1196, 1713, 0),(1196, 1712, 0),(1196, 1711, 0),(1196, 1710, 0),(1196, 1709, 0),(1196, 1708, 0),(1196, 1707, 0),(1196, 1706, 0),(1196, 1705, 0),]
    if type(path) != type(None) :
        for p in path:
            wx = remap(p[0], 0, 512, -512, -256)
            wy = remap(p[1], 0, 512, 256, 512)
            costs_arr[p[0]][p[1]] = 50*(p[2]+1)
            print(wx, wy)
    

    print(arr)
    image = Image.fromarray((arr*255).astype(numpy.uint8), mode="L")
    image.save("test.png")
    pyplot.imshow(costs_arr)
    pyplot.show()