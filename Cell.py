from OnTile import OnTile
from utils import type_to_name
import json


class Cell:
    def __init__(self, tile):
        self.__structure__ = None
        self.__object__ = None
        self.__road__ = None
        self.__tile__ = tile
        self.__resources_matrix__ = [0, 0, 0, 0]

    def diff_resources(self,resources):
        for i in range(len(self.__resources_matrix__)):
            self.__resources_matrix__[i]=max(0,self.__resources_matrix__[i]-resources[i])

    def add_OnTile(self, on_tile):
        if on_tile.__type__ == "Road" and self.__road__ == None:
            self.__road__ = on_tile
            return True
        else:
            if on_tile.__is_structure__ == True:
                if self.__structure__ == None:
                    self.__structure__ = on_tile
                    return True
            else:
                if self.__structure__ != None and on_tile.__type__ == "Person":
                    self.__structure__.add_people(on_tile)
                elif self.__object__ == None or self.__object__==on_tile:
                    self.__object__ = on_tile
                    return True
        return False

    def selected_category(self):

        if self.__structure__ != None:
            return self.__structure__.__type__
        if self.__object__ != None:
            if self.__object__.__type__ == "Person":
                return "People"
            return self.__object__.__type__
        if self.__road__ != None:
            return "Road"

        return type_to_name(self.__tile__.__type__)

    def manufacture(self, on_tile):
        if self.__object__ == None:
            self.__object__ = on_tile
            return True
        return False

    def selected_complete(self):
        if self.__structure__ != None:
            return self.__structure__.__is_complete__
        return False

    def selected_people(self):
        if self.__structure__ != None:
            return len(self.__structure__.__people__)
        if self.__object__.__object__.__type__ == "Person":
            return 1
        return 0

    def can_add_OnTile(self, on_tile):
        # if self.__tile__.__type__!=2:
        if on_tile.__is_structure__ == True:
            if self.__structure__ == None and self.__tile__.__type__ == 1:
                return True
        else:
            if on_tile.__type__ == "Road":
                return self.__road__ == None and self.__tile__.__type__ == 1
            if self.__object__ == None or self.__object__==on_tile:
                    # and (
                    # on_tile.__type__ in ["Car", "Truck"] and (self.__road__ != None or self.__structure__!=None) or on_tile.__type__ in ["Helicopter",
                    #                                                                                        "Person"]):
                return True
        return False

    def move_person(self, x, y):
        if self.__structure__ != None:
            self.__structure__.remove_person(x, y)
        elif self.__object__ != None and self.__object__.__type__ == "Person":
            self.__object__ = None

    def deposit(self, resources_matrix):
        if self.__structure__ != None:
            deposited = self.__structure__.deposit(resources_matrix)
            return deposited

    def remove_onTile(self, on_tile):
        if self.__object__!=None:
            if on_tile.__type__ == self.__object__.__type__:
                if on_tile.__type__ == "Person":
                    self.__object__ = None
            elif on_tile.__type__ == "Person":
                self.__object__.remove_person(on_tile)
            else:
                self.__object__ = None

    def get_resources(self):
        if self.__structure__ != None:
            return self.__structure__.__storage__
        elif self.__object__ != None and self.__object__.__type__ == "Person":
            return self.__object__.__resources_matrix__
        else:
            return [-1]

    def make_empty(self):
        if self.__structure__ != None:
            self.__structure__.make_empty()

    def selected_by_type(self, type):
        if self.__object__ != None and self.__object__.__type__ == type:
            return 1
        return 0

    def take_away(self, deposited):
        if self.__structure__ != None:
            self.__structure__.take_away(deposited)
        else:
            if self.__tile__.__type__ != 1:
                for i in range(len(deposited)):
                    if deposited[1] > 0:
                        self.__tile__.__resources__ = min(0, self.__tile__.__resources__ - deposited[i])

    def take_resources(self, on_tile):
        f = open('./configuration.json')
        dict = json.load(f)
        if (
                self.__tile__ != None or self.__structure__ != None) and on_tile != None and on_tile.__is_structure__ == False:
            if on_tile.__type__ == "Person":
                capacity = [1, 1, 1, 1]
            else:
                capacity = dict["Capacities"][on_tile.__type__]
            if self.__structure__ != None:
                matrix = self.__structure__.__storage__
            else:
                matrix = self.__tile__.__resources_matrix__
            left_capacity=on_tile.__resources_matrix__
            for i in range(len(left_capacity)):
                left_capacity[i]=capacity[i]-left_capacity[i]
            capacity=left_capacity
            for i, j in zip(range(len(matrix)), capacity):
                if matrix[i] > 0:
                    matrix[i] = max(0, matrix[i] - j)
            if self.__structure__ != None:
                self.__structure__.__storage__ = matrix
            else:
                self.__tile__.__resources_matrix__ = matrix
                for id in matrix:
                    if id != 0:
                        self.__tile__.__resources__ = id
