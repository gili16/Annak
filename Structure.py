import json
from OnTile import OnTile
from resources_dict import resources_index


class Structure(OnTile):
    def __init__(self, coordinates, type):
        f = open('./configuration.json')
        sizes = json.load(f)["Sizes"]
        super().__init__(coordinates, type, sizes[type], True)
        self.__storage__ = [0, 0, 0, 0]
        self.__people__ = []
        self.__is_complete__ = False
        self.__type__ = type


    def add_people(self, person):
        f = open('./configuration.json')
        dict = json.load(f)
        index = resources_index["People"]
        max_size = dict["Capacities"][self.__type__][index]
        if len(self.__people__) < max_size:
            self.__people__ += [person]

    def remove_person(self, x, y):
        l = len(self.__people__)
        for p in range(l):
            if self.__people__[p].__coordinates__[0] == x and self.__people__[p].__coordinates__[1] == y:
                self.__people__.pop(p)
                break

    def deposit(self, resource_matrix):
        f = open('./configuration.json')
        dict = json.load(f)
        deposited = [0, 0, 0, 0]
        for i in range(len(resource_matrix)):

            max_size = dict["Capacities"][self.__type__][i]
            prev = self.__storage__[i]
            if prev == max_size:
                deposited[i] = 0
            elif prev + resource_matrix[i] > max_size:
                self.__storage__[i] = max_size
                deposited[i] = max_size - prev
            else:
                self.__storage__[i] = prev + resource_matrix[i]
                deposited[i] = resource_matrix[i]
        return deposited

    def make_empty(self):
        self.__storage__ = [0, 0, 0, 0]
        self.__people__ = []

    def take_away(self, deposited):
        for i in range(len(deposited)):
            self.__storage__[i] -= deposited[i]
