from Board import Board
from utils import read_multiple_lines, type_to_name, get_resource_from_type, values_in_matrix, read_steps_input, \
    name_to_type, resources_matrix_to_string
from Tile import Tile
import json
import sys
from resources_dict import dict, resources_index
from Person import Person
from Structure import Structure
from Road import Road
from gui import Gui
import random


class Game:

    def __init__(self):
        f = open('./configuration.json')
        self.__sizes__ = json.load(f)["Sizes"]
        self.__board__ = Board()
        self.__selected_coordinates__ = []
        self.__tiles__ = []
        self.__selected_tile__ = None
        self.__selected_cell__ = None
        self.__steps__ = []
        self.__is_over__ = False
        self.__cityCount__ = 0
        self.__villageCount__ = 0
        self.__roadCount__ = 0
        self.__roadCount__ = 0
        self.__carCount__ = 0
        self.__truckCount__ = 0
        self.__helicopterCount__ = 0
        self.__my_resources__ = [0, 0, 0, 0, 0, 0]
        self.__rain__ = 0
        self.__selected_element__ = None
        self.__points__ = 0
        self.__points_set__ = False
        self.__curr_line = 0
        self.__gui = None

    def init_world(self, tiles):
        self.__tiles__ = [
            [Tile(tiles[row][col], 0, [col, row]) for col in range(len(tiles[row]))] for
            row in range(len(tiles))]
        self.__board__.init_tiles(self.__tiles__)
        self.__gui = Gui(self.__tiles__, self.__board__)

    def select_tile(self, x, y):
        tile_size = self.__sizes__["Tile"][0]
        self.__selected_tile__ = self.__tiles__[int(y - 1) // tile_size][int(x - 1) // tile_size]
        self.__selected_coordinates__ = [int(x), int(y)]

    def __tic__(self, num=1):
        for tile in self.__tiles__:
            for col in tile:
                col.add_tic(num)
        self.__board__.tic()

    def read_input_stdin(self):
        inp = input()
        return inp

    def read_input_file(self):
        lines = []
        with open('./input.txt') as f:
            lines = f.readlines()
        self.__curr_line += 1
        if self.__curr_line - 1 < len(lines):
            return lines[self.__curr_line - 1].strip('\n')
        else:
            raise EOFError

    def play(self):
        last_inp = []
        last_command = ""
        current_command = ""
        while not self.__is_over__:
            try:
                inp = self.read_input_file()
                if inp and inp != '' and inp != ' ' and inp != '\n' and len(inp) > 0:
                    if inp.startswith('+'):
                        last_command = current_command
                        current_command = inp
                    if not inp.startswith('+') or last_command != "" and current_command != last_command:

                        if current_command == '+World':
                            last_inp += [inp]
                        elif len(last_inp) > 0:
                            self.__steps__ += read_steps_input([last_command] + last_inp)
                            last_inp = []
                            if current_command != inp:
                                self.__steps__ += read_steps_input([current_command] + [inp])
                        else:
                            self.__steps__ += read_steps_input([current_command] + [inp])
                else:
                    raise EOFError
                while len(self.__steps__) > 0:
                    results = self.__steps__[0].execute()
                    self.__tic__(len(results))
                    if self.__rain__ > 0:
                        self.__rain__ -= len(results)
                        if self.__rain__ < 0:
                            self.__rain__ = 0
                    is_start = current_command == "+Start"
                    if current_command == "+Asserts":
                        if not results[1]:
                            self.handle_execute_result(results, is_start)
                    else:
                        self.handle_execute_result(results, is_start)

                    self.__steps__.pop(0)
                if self.__gui and len(self.__tiles__) > 0:
                    self.__gui.show_canvas()
            except EOFError:
                select_coordinates = [-1, -1]
                while not self.__gui.HAS_MOVE:
                    elements = self.__board__.get_moveable_elements()
                    for element in elements:
                        if not element.has_more_moves():
                            width, height = len(self.__tiles__[0]) * 5, len(self.__tiles__) * 5
                            x = random.randint(0, width - 1)
                            y = random.randint(0, height - 1)
                            self.select_cell(element.__coordinates__[0], element.__coordinates__[1])
                            self.__selected_element__ = element
                            self.move(x, y)
                    self.__tic__()
                    if self.__gui:
                        wait = 500
                        count_loop = 1
                        while wait > 0:
                            self.__tic__()
                            if self.__rain__ > 0:
                                self.__rain__ -= 1
                            wait -= 1
                            if count_loop % 50 == 0:
                                if len(self.__tiles__) > 0:
                                    select_coordinates = self.__gui.show_canvas()
                            count_loop += 1

                    print(select_coordinates)
                self.select_cell(self.__gui.__rec_coordinates__[0] + 1, self.__gui.__rec_coordinates__[1] + 1)
                matrix = self.resources_matrix(None)
                self.__gui.__resources_changed__ = True
                self.__gui.__selected_resources__ = matrix
                elements_to_move = self.__board__.elements_in_rec(self.__gui.__rec_coordinates__[0],
                                                                  self.__gui.__rec_coordinates__[1],
                                                                  self.__gui.__rec_size__[0],
                                                                  self.__gui.__rec_size__[1])
                for element in elements_to_move:
                    self.select_cell(element.__coordinates__[0] + 1, element.__coordinates__[1] + 1)
                    self.__selected_element__ = element
                    self.move(Gui.SELECTED_COORDINATES[0], Gui.SELECTED_COORDINATES[1])
                wait = 500
                count_loop = 1
                while wait > 0:
                    self.__tic__()
                    if self.__rain__ > 0:
                        self.__rain__ -= 1
                    wait -= 1
                    if count_loop % 50 == 0:
                        if self.__gui and len(self.__tiles__) > 0:
                            self.__gui.show_canvas()
                    count_loop += 1
                break

    def handle_execute_result(self, result, is_start):
        if result:
            if result[0] == "World":
                self.init_world(result[1])
            elif result[0] == "Select":
                self.select_cell(result[1][0], result[1][1])
            elif result[0] == "SelectedCategory":
                print("SelectedCategory", self.__selected_cell__.selected_category())
            elif result[0] == "SelectedComplete":
                print("SelectedComplete", self.__selected_cell__.selected_complete())
            elif result[0] == "SelectedPeople":
                print("SelectedPeople", self.__selected_cell__.selected_people())
            elif result[0] == "SelectedTruck":
                print("SelectedTruck", self.__selected_cell__.selected_by_type("Truck"))
            elif result[0] == "SelectedCar":
                print("SelectedCar", self.__selected_cell__.selected_by_type("Car"))
            elif result[0] == "Manufacture":
                flag, resources = self.__board__.manufacture(result[1][0], result[1][1], result[1][2], is_start,
                                                             self.__my_resources__)

                if flag:
                    if result[1][0] == "Car":
                        self.__carCount__ += 1
                    elif result[1][0] == "Truck":
                        self.__truckCount__ += 1
                    else:
                        self.__helicopterCount__ += 1
                    self.__my_resources__ = resources
            elif result[0] == "CarCount":
                print('CarCount', self.__carCount__)
            elif result[0] == "TruckCount":
                print("TruckCount", self.__truckCount__)
            elif result[0] == "HelicopterCount":
                print("HelicopterCount", self.__helicopterCount__)
            elif result[0] == "Resource":
                self.add_resource(result[1][1], int(result[1][0]), int(result[1][2]), int(result[1][3]))
            elif result[0] == "SelectedResource":
                print("SelectedResource",
                      resources_matrix_to_string(self.get_resources(self.__selected_coordinates__[0],
                                                                    self.__selected_coordinates__[
                                                                        1])))
            elif result[0] == "People":
                self.add_people(int(result[1][0]), int(result[1][1]), int(result[1][2]))
            elif result[0] == "Work":
                self.work(int(result[1][0]), int(result[1][1]))
            elif result[0] == "Rain":
                self.__rain__ = int(result[1][0])
            elif result[0] == "Build":
                self.build(result[1][0], int(result[1][1]), int(result[1][2]), is_start)
            elif result[0] == "Deposit":
                self.deposit(int(result[1][0]), int(result[1][1]))
            elif result[0] == "CityCount":
                print("CityCount", self.__cityCount__)
            elif result[0] == "VillageCount":
                print("VillageCount", self.__villageCount__)
            elif result[0] == "RoadCount":
                print("RoadCount", self.__roadCount__)
            elif result[0] == "Resources":
                self.add_my_resources(result[1])
            elif result[0] == "SelectedCoordinates":
                self.selected_coordinates()
            elif result[0] == "TakeResources":
                self.take_resource(int(result[1][0]), int(result[1][1]))
            elif result[0] == "Wait":
                wait = int(result[1][0])
                count_loop = 1
                while wait > 0:
                    self.__tic__()
                    if self.__rain__ > 0:
                        self.__rain__ -= 1
                    wait -= 1
                    if count_loop % 50 == 0:
                        if self.__gui and len(self.__tiles__) > 0:
                            self.__gui.show_canvas()
                    count_loop += 1
            elif result[0] == "Move":
                self.move(int(result[1][0]), int(result[1][1]))
            elif result[0] == "SetPoints":
                self.__points__ = int(result[1][0])
                self.__points_set__ = True
            elif result[0] == "Points":
                print(f"Points {self.__points__}")

    def add_resource(self, resource, amount, x, y):
        tile_size = self.__sizes__["Tile"][0]
        tile = self.__tiles__[int(y - 1) // tile_size][int(x - 1) // tile_size]
        if self.__board__.select(int(x), int(y)).__structure__ == None:
            if self.__board__.select(int(x), int(y)).__object__ != None:
                self.__board__.select(int(x), int(y)).__object__.add_resource(resource, amount)
            else:
                tile.__resources__ += amount
                index = resources_index[resource]
                tile.__resources_matrix__[index] += amount
                cell = self.__board__.select(x, y)
                cell.__resources_matrix__[index] += amount
        elif self.__board__.select(int(x), int(y)).__structure__ != None:
            cell = self.__board__.select(int(x), int(y)).__structure__
            index = resources_index[resource]
            cell.__storage__[index] += amount

    def add_people(self, amount, x, y):
        self.__selected_cell__ = self.__board__.select(x, y)
        for i in range(amount):
            self.__board__.add_OnTile(Person([x, y]), x, y)

    def build(self, category, x, y, is_start):
        if is_start or category in ["Village", "City"] and self.__board__.there_is_road_to_city(x, y, self.__sizes__[
            category][0], self.__sizes__[category][1]):
            if category in ["Village", "City"]:
                points = 0
                if self.__points_set__:
                    points = -1
                if self.__board__.add_OnTile(Structure([x, y], category), x, y):
                    if category == "Village":
                        self.__villageCount__ += 1
                        points += 1
                    else:
                        self.__cityCount__ += 1
                        points += 2
                    self.__points__ += points
            else:
                if self.__board__.add_OnTile(Road([x, y]), x, y):
                    self.__roadCount__ += 1
        elif category == "Road":
            if self.__board__.add_OnTile(Road([x, y]), x, y):
                self.__roadCount__ += 1

    def work(self, x, y):
        tile_size = self.__sizes__["Tile"][0]
        tile = self.__tiles__[int(y - 1) // tile_size][int(x - 1) // tile_size]
        if self.__selected_cell__.__object__.__type__ == "Person":
            if self.__board__.select(x, y).can_add_OnTile(self.__selected_cell__.__object__):
                # self.__selected_cell__.__object__.move([x, y])
                # self.__selected_cell__.move_person(x, y)
                self.__board__.move(self.__selected_element__, x, y)
                if type_to_name(tile.__type__) == "Ground":
                    self.__selected_element__.connect_resources(tile.__resources_matrix__)
                else:
                    self.__selected_element__.add_resource(dict[type_to_name(tile.__type__)], 1)
                # tile.__resources__ -= diff
                cell = self.__board__.select(x, y)
                cell.diff_resources(self.__selected_element__.__resources_matrix__)
                tile.diff_resources(self.__selected_element__.__resources_matrix__)
                # cell.__resources_matrix__ = self.diff_resources(cell.__resources_matrix__,
                #                                                 self.__selected_element__.__resources_matrix__)
                # tile.__resources_matrix__ = self.diff_resources(tile.__resources_matrix__,
                #                                                 self.__selected_element__.__resources_matrix__)
        if tile.__resources__ < 0:
            tile.__resources__ = 0

    def resources_matrix(self, tile):
        matrix = [0, 0, 0, 0]
        if self.__selected_cell__.__structure__ != None:
            return self.__selected_cell__.__structure__.__storage__
        if self.__selected_cell__.__object__ != None and self.__selected_cell__.__object__.__type__ == "Person":
            matrix = self.__selected_cell__.__object__.__resources_matrix__
        if tile:
            self.connect_resources(matrix, tile.__resources_matrix__)
        return matrix

    def select_cell(self, x, y):
        self.__selected_cell__ = self.__board__.select(x, y)
        self.__selected_coordinates__ = [int(x), int(y)]
        self.__selected_element__ = self.__selected_cell__.__object__

    def deposit(self, x, y):
        resources = self.get_resources(self.__selected_coordinates__[0], self.__selected_coordinates__[1])
        tile_size = self.__sizes__["Tile"][0]
        tile = self.__tiles__[int(y) - 1 // tile_size][int(x) - 1 // tile_size]
        cell = self.__board__.select(x, y)
        deposited = cell.deposit(resources)
        self.__selected_cell__.take_away(deposited)

    def get_resources(self, x, y):
        resources = self.__board__.select(x, y).get_resources()
        if resources[0] != -1:
            return resources
        tile_size = self.__sizes__["Tile"][0]
        tile = self.__tiles__[int(y - 1) // tile_size][int(x - 1) // tile_size]
        return tile.__resources_matrix__

    def make_empty(self, x, y):
        self.__board__.select(x, y).make_empty()

    def take_resource(self, x, y):
        # resources = self.get_resources(self.__selected_coordinates__[0], self.__selected_coordinates__[1])
        # tile_size = self.__sizes__["Tile"][0]
        # tile = self.__tiles__[int(y - 1) // tile_size][int(x - 1) // tile_size]
        cell = self.__board__.select(x, y)
        # if cell.__structure__ != None and self.__selected_cell__.__tile__.__resources__ == 0:
        cell.take_resources(self.__selected_cell__.__object__)

    def add_my_resources(self, resources_matrix):
        for i in range(len(resources_matrix)):
            self.__my_resources__[i] += int(resources_matrix[i])

    def selected_coordinates(self):
        if len(self.__tiles__) > 0 and self.__selected_element__ != None:
            x, y = self.__selected_element__.__coordinates__
            index_x, index_y = self.compute_tile_indices(x, y)
            if self.__selected_element__.__type__ == "Car" or self.__selected_element__.__move_stopped__ == "Car":
                print(f'SelectedCoordinates {x} {y}')
            else:
                print(f'SelectedCoordinates {x // 5} {y // 5}')
        else:
            print("SelectedCoordinates 0 0")

    def move(self, x, y):
        if self.__selected_element__ != None:
            if self.__selected_element__.__type__ == "Person":
                person = self.__selected_element__
                self.connect_resources(person.__resources_matrix__, self.__selected_cell__.__resources_matrix__)
            self.__board__.move(self.__selected_element__, x, y)

    def connect_resources(self, res1, res2):
        for i in range(len(res1)):
            res1[i] += res2[i]

    def diff_resources(self, res1, res2):
        for i in range(len(res1)):
            res1[i] = max(0, res1[i] - res2[i])
        return res1

    def compute_tile(self, x, y):
        tile_size = self.__sizes__["Tile"][0]
        tile = self.__tiles__[int(y - 1) // tile_size][int(x - 1) // tile_size]
        return tile

    def compute_tile_indices(self, x, y):
        tile_size = self.__sizes__["Tile"][0]
        return (int(y - 1) // tile_size), (int(x - 1) // tile_size)
