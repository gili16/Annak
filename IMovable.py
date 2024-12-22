from OnTile import OnTile
import json
from resources_dict import dict, resources_index
from utils import bresenham


class IMoveable(OnTile):
    def __init__(self, coordinates, type):
        f = open('./configuration.json')
        config_dict = json.load(f)
        sizes = config_dict["Sizes"]
        config_type = type
        if type == "Person":
            config_type = "People"
        self.__speed__ = config_dict["Speeds"][config_type]
        super().__init__(coordinates, type, sizes[config_type], False)
        self.__resources_matrix__ = [0, 0, 0, 0]
        self.__move_toward__ = coordinates
        self.__steps_left__ = []
        self.__tics_to_step__ = -1
        self.__move_stopped__ = ""

    def move(self, coordinates, steps):
        if coordinates != self.__coordinates__:
            self.__move_toward__ = coordinates
            if not steps or len(steps) == 0:
                self.__steps_left__ = bresenham(self.__coordinates__[0], self.__coordinates__[1], coordinates[0],
                                                coordinates[1])
                self.__steps_left__.pop(0)
            else:
                self.__steps_left__ = steps
            self.__tics_to_step__ = 1 // self.__speed__

    def add_resource(self, resource_name, amount):
        f = open('./configuration.json')
        capacity = [1, 1, 1, 1]
        if self.__type__ != "Person":
            capacity = json.load(f)["Capacities"][self.__type__]
        original_amount = self.__resources_matrix__[resources_index[resource_name]]
        self.__resources_matrix__[resources_index[resource_name]] = min(
            self.__resources_matrix__[resources_index[resource_name]] + amount,
            capacity[resources_index[resource_name]])
        return self.__resources_matrix__[resources_index[resource_name]] - original_amount

    def tic(self,is_water):
        self.__tics_to_step__ -= 1
        if self.__tics_to_step__ == 0 and self.__move_toward__ != self.__coordinates__ and len(
                self.__steps_left__) > 0 and (not is_water or is_water and len(self.__steps_left__)>1):
            return self.__steps_left__[0]
        else:
            return [-1, -1]

    def move_one_step(self,is_water):
        self.__tics_to_step__ = 1 // self.__speed__
        if not is_water or is_water and len(self.__steps_left__)!=1:
            self.__coordinates__ = self.__steps_left__[0]
        return self.__steps_left__.pop(0)

    def no_more_move(self,i_stopped_u):
        self.__tics_to_step__ = -1
        self.__move_toward__ = self.__coordinates__
        self.__steps_left__ = []
        self.__move_stopped__ = i_stopped_u

    def connect_resources(self, res2):
        f = open('./configuration.json')
        capacity = [1, 1, 1, 1]
        if self.__type__ != "Person":
            capacity = json.load(f)["Capacities"][self.__type__]
        for i in range(len(self.__resources_matrix__)):
            self.__resources_matrix__[i]= min(capacity[i],self.__resources_matrix__[i]+res2[i])

    def has_more_moves(self):
        return len(self.__steps_left__)>0 and self.__move_toward__!=self.__coordinates__