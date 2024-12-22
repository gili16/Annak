import json
import utils
from OnTile import OnTile
from Tile import Tile
from utils import type_to_name, get_resource_from_type, euclidean_distance, get_surrounding_pixels
from resources_dict import dict as resources_map
from Cell import Cell
from Vehicle import Vehicle


class Board:

    def __init__(self):
        f = open('./configuration.json')
        self.__sizes__ = json.load(f)["Sizes"]
        self.__board__ = []
        self.__elements__ = []
        self.__tiles__ = []

    def init_tiles(self, tiles):
        self.__tiles__ = tiles
        tile_size = self.__sizes__["Tile"][0]
        tiles_count = utils.values_in_matrix(tiles)
        self.__board__ = [[None for _ in range(self.__sizes__["Tile"][1] * tiles_count)] for _ in
                          range(self.__sizes__["Tile"][0] * tiles_count)]
        for row in range(len(tiles)):
            for col in range(len(tiles[row])):
                for i in range(tile_size):
                    for j in range(tile_size):
                        self.__board__[row * tile_size + i][col * tile_size + j] = Cell(tiles[row][col])

    def select(self, x, y):
        if int(x) - 1 >= len(self.__board__[0]) or int(y) - 1 >= len(self.__board__):
            return None
        return self.__board__[int(y) - 1][int(x) - 1]

    def remove_onTile(self, on_tile):
        x, y = on_tile.__coordinates__
        for i in range(y - 1, y - 1 + on_tile.__size__[0]):
            for j in range(x - 1, x - 1 + on_tile.__size__[1]):
                self.__board__[i][j].remove_onTile(on_tile)

    def can_add_onTile(self, on_tile, x, y):
        if y - 1 + on_tile.__size__[0] > len(self.__board__) or x - 1 + on_tile.__size__[1] > len(self.__board__[0]):
            return False
        for i in range(y - 1, min(y - 1 + on_tile.__size__[0], len(self.__board__))):
            for j in range(x - 1, min(x - 1 + on_tile.__size__[1], len(self.__board__[i]))):
                if not self.__board__[i][j].can_add_OnTile(on_tile):
                    return False
        return True

    def add_OnTile(self, on_tile, x, y):
        if self.can_add_onTile(on_tile, x, y):
            self.remove_onTile(on_tile)
            for i in range(y - 1, y - 1 + on_tile.__size__[0]):
                for j in range(x - 1, x - 1 + on_tile.__size__[1]):
                    self.__board__[i][j].add_OnTile(on_tile)
            self.__elements__ += [on_tile]
            return True
        return False

    def manufacture(self, category, x, y, is_start, resources):
        if is_start:
            on_tile = Vehicle([int(x), int(y)], category)
            return self.add_OnTile(on_tile, int(x), int(y)), resources
        else:
            f = open('./configuration.json')
            costs = json.load(f)["Costs"][category]
            original_resources = resources.copy()
            for i, j in zip(range(len(resources)), costs):
                if j > resources[i]:
                    return False, original_resources
                else:
                    resources[i] -= j
            on_tile = Vehicle([int(x), int(y)], category)
            return self.add_OnTile(on_tile, int(x), int(y)), resources

    def tic(self):
        for element in self.__elements__:
            if not element.__is_structure__ and len(element.__steps_left__) > 0:
                y, x = self.compute_tile_indices(element.__steps_left__[0][0] + 1,
                                                 element.__steps_left__[0][1] + 1)
                is_water = len(element.__steps_left__) > 0 and self.__tiles__[x - 1][y - 1].__type__ == 2
                coordinates = element.tic(is_water)
                if coordinates != [-1, -1]:
                    if self.add_OnTile(element, coordinates[0]+1, coordinates[1]+1) or element.__type__ == "Helicopter":
                        is_water = self.select(coordinates[0]+1, coordinates[1]+1).__tile__.__type__ == 2
                        element.move_one_step(is_water)
                        if self.select(coordinates[0]+1, coordinates[1]+1).__structure__ != None:
                            if self.select(coordinates[0]+1, coordinates[1]+1).__structure__ == self.select(
                                    element.__move_toward__[0], element.__move_toward__[1]).__structure__:
                                element.no_more_move("Structure")
                            # if element.__type__ == "Person":
                            #     self.select(coordinates[0], coordinates[1]).__structure__.add_people(element)
                    else:
                        element.no_more_move(
                            self.type_of_occupping(element, element.__size__, coordinates[0], coordinates[1]))

    def there_is_next_road(self, vehicle, next_step):
        if self.can_add_onTile(vehicle, next_step[0], next_step[1]):
            x, y = next_step
            for i in range(y - 1, y - 1 + vehicle.__size__[0]):
                for j in range(x - 1, x - 1 + vehicle.__size__[1]):
                    if self.select(i, j).__road__ == None:
                        return False
            return True
        return False

    def find_road(self, vehicle, source, current, destination):
        if current == destination:
            return 0, []

        left = [current[0] - 1, current[1]]
        right = [current[0] + 1, current[1]]
        up = [current[0], current[1] - 1]
        down = [current[0], current[1] + 1]
        min_road = [current]
        min_distance = -1

        if left != source and self.there_is_next_road(vehicle, left):
            result, road = self.find_road(vehicle, current, left, destination)
            if min_distance == -1 or result < min_distance:
                min_distance = result
                min_road = [current] + road
                if min_distance == 0:
                    return 0, min_road

        if up != source and self.there_is_next_road(vehicle, up):
            result, road = self.find_road(vehicle, current, up, destination)
            if min_distance == -1 or result < min_distance:
                min_distance = result
                min_road = [current] + road
                if min_distance == 0:
                    return 0, min_road

        if right != source and self.there_is_next_road(vehicle, right):
            result, road = self.find_road(vehicle, current, right, destination)
            if min_distance == -1 or result < min_distance:
                min_distance = result
                min_road = [current] + road
                if min_distance == 0:
                    return 0, min_road

        if down != source and self.there_is_next_road(vehicle, down):
            result, road = self.find_road(vehicle, current, down, destination)
            if min_distance == -1 or result < min_distance:
                min_distance = result
                min_road = [current] + road
                if min_distance == 0:
                    return 0, min_road

        if min_distance == -1:
            min_distance = euclidean_distance(current[0], current[1], destination[0], destination[1])
        return min_distance, min_road

    def move(self, on_tile, x, y):
        if on_tile.__is_structure__ == False:
            if on_tile.__type__ in ["Helicopter", "Person"]:
                on_tile.move([x, y], [])
            elif on_tile.__type__ in ["Car", "Truck"]:
                steps = []
                # steps = self.find_road(on_tile, on_tile.__coordinates__, on_tile.__coordinates__, [x, y])
                on_tile.move([x, y], steps)

    def exists(self, lst, value):
        for item in lst:
            if item == value:
                return True
        return False

    def get_range_to_road(self, surrounding_cell):
        offset = [0, 0]
        if self.exists(surrounding_cell[2], "Bottom") or self.exists(surrounding_cell[2], "Top"):
            offset[0] = 1
        elif self.exists(surrounding_cell[2], "Left") or self.exists(surrounding_cell[2], "Right"):
            offset[1] = 1
        cells_to_check = [[surrounding_cell[0], surrounding_cell[1]]]
        for i in range(1, 5):
            cells_to_check += [[cells_to_check[i - 1][0] + offset[0], cells_to_check[i - 1][1] + offset[1]]]
        return cells_to_check

    def there_is_road_to_city(self, x, y, width, height):
        surrounding_cells = get_surrounding_pixels(x, y, height, width, len(self.__board__[0]), len(self.__board__))
        for i in surrounding_cells:
            if self.select(i[0], i[1]) and self.select(i[0], i[1]).__road__ != None:
                cells_to_check = self.get_range_to_road(i)
                flag = True
                for cell in cells_to_check:
                    if self.select(cell[0], cell[1]) == None or self.select(cell[0],
                                                                            cell[1]).__road__ == None:
                        flag = False
                        break
                if flag:
                    return True
        return False

    def type_of_occupping(self, me, size, x, y):
        for i in range(y, y + size[0]):
            for j in range(x, x + size[1]):
                if self.select(j + 1, i + 1).__object__ != None and self.select(j + 1,
                                                                                i + 1).__object__.__coordinates__ != me.__coordinates__:
                    return self.select(j + 1, i + 1).__object__.__type__
        return None

    def get_moveable_elements(self):
        elements = []
        for element in self.__elements__:
            if not element.__is_structure__:
                elements += [element]
        return elements

    def get_structure_elements(self):
        elements = []
        for element in self.__elements__:
            if element.__is_structure__:
                elements += [element]
        return elements

    def get_board_size(self):
        return [len(self.__board__[0]), len(self.__board__)]

    def compute_tile_indices(self, x, y):
        tile_size = self.__sizes__["Tile"][0]
        return (int(y - 1) // tile_size), (int(x - 1) // tile_size)

    def elements_in_rec(self, x, y, width, height):
        elements = []
        for element in self.get_moveable_elements():
            if x <= element.__coordinates__[0] <= x+width and y <= element.__coordinates__[1] <= y+height:
                elements += [element]
        return elements
