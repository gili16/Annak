import json
import sys
from resources_dict import dict as resources_map
from Step import Step
import math


def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def type_to_name(type):
    f = open('./configuration.json')
    tiles_dict = json.load(f)["Tiles"]
    for key, value in tiles_dict.items():
        if value == type:
            return key


def name_to_type(name):
    f = open('./configuration.json')
    tiles_dict = json.load(f)["Tiles"]
    return tiles_dict[name]


def read_multiple_lines():
    input_data = sys.stdin.read()
    return input_data


def values_in_matrix(matrix):
    # print(matrix)
    count = 0
    for row in matrix:
        for _ in row:
            count += 1
    return count


def get_resource_from_type(type):
    name = type_to_name(type)
    if name in resources_map:
        return resources_map[name]
    else:
        return None


def read_steps_input(inp):
    steps = []
    flag = False
    # if len(inp)>0:
    #     inp.pop(0)
    # print(type(inp))
    i = 0
    while i < len(inp):
        result = []
        line = inp[i]
        while line and not flag or line[0] != '+':
            flag = True
            result += [line]
            i += 1
            if i == len(inp):
                break
            line = inp[i]
        steps += [Step(result)]
        flag = False
    return steps


def resources_matrix_to_string(resources):
    st = ""
    for resource in resources:
        st += str(resource) + " "
    return st


def find_min(array):
    min = array[0]
    mini = 0
    for i in range(len(array)):
        if array[i] < min:
            min = array[i]
            mini = i
    return mini


def find_max(array):
    max = array[0]
    maxi = 0
    for i in range(len(array)):
        if array[i] < max:
            max = array[i]
            maxi = i
    return maxi


def bresenham(x1, y1, x2, y2):
    points = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    return points


def get_surrounding_pixels(x, y, width, height, n, m):
    surrounding_pixels = []

    # Top border
    for i in range(x, x + width):
        if 1 <= i <= n and 1 <= y - 1 <= m:
            surrounding_pixels.append((i, y - 1, ["Top"]))

    # Bottom border
    for i in range(x, x + width):
        if 0 < i <= n and 0 < y + height <= m:
            surrounding_pixels.append((i, y + height, ["Bottom"]))

    # Left border
    for j in range(y, y + height):
        if 0 < x - 1 <= n and 0 < j <= m:
            surrounding_pixels.append((x - 1, j, ["Left"]))

    # Right border
    for j in range(y, y + height):
        if 0 < x + width <= n and 0 < j <= m:
            surrounding_pixels.append((x + width, j, ["Right"]))

    # Avoid duplicates at corners and ensure corners are added if within bounds
    # corners = [(x - 1, y - 1, ["Top", "Left"]), (x + width, y - 1, ["Top", "Right"]),
    #            (x - 1, y + height, ["Left", "Bottom"]),
    #            (x + width, y + height, ["Bottom", "Right"])]
    # for corner in corners:
    #     if 0 <= corner[0] < n and 0 <= corner[1] < m:
    #         surrounding_pixels.append(corner)

    return surrounding_pixels
