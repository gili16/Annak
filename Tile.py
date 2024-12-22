import json
from resources_dict import dict
from utils import type_to_name,find_min,find_max


class Tile:
    def __init__(self, type, resources, start):
        self.__type__ = type
        self.__resources__ = resources
        self.__tic__ = 0
        self.__start__ = start
        self.__resources_matrix__=[0,0,0,0]
        # self.__people__=0
        # self.__Objects__=[]

    def add_tic(self,num=1):
        self.__tic__ += num
        f = open('./configuration.json')
        if self.__type__ in range(3,5):
            if json.load(f)["Rains"][dict[type_to_name(self.__type__)]] == self.__tic__:
                self.__tic__ = 0
                self.__resources__ +=1 # json.load(f)["StartingResource"][type_to_name(self.__type__)]
                if type_to_name(self.__type__) == "Forest":
                    self.__resources_matrix__[0]+=1
                elif type_to_name(self.__type__) == "Field":
                    self.__resources_matrix__[1]+=1
                elif type_to_name(self.__type__) == "IronMine":
                    self.__resources_matrix__[2]+=1
                elif type_to_name(self.__type__) == "BlocksMine":
                    self.__resources_matrix__[3]+=1

    def __str__(self):
        return f"type:{self.__resources__}\nresources:{self.__resources__}\nstart:{self.__start__}\ntic:{self.__tic__}\n"

    def diff_resources(self,resources):
        for i in range(len(self.__resources_matrix__)):
            self.__resources_matrix__[i]=max(0,self.__resources_matrix__[i]-resources[i])

    # def has_common(self,range1,range2):
    #     min1=find_min(range(range1+1))
    #     min2=find_min(range(range2+1))
    #     max1=find_max(range(range1+1))
    #     max2=find_max(range(range2+1))
    #     for i in range(max(min1,min2),min(max1,max2)):
    #         if range1[i]==range2[i]:
    #             return True
    #     return False
    #
    #
    # def is_available(self,coordinates,is_structure,size):
    #     for ob in self.__Objects__:
    #         if is_structure==ob.__is_structure__ and self.has_common(range(ob.__coordinates__[0],ob.__coordinates__[0]+ob.__size__[0]+1),range(coordinates[0],coordinates[0]+size[0]+1)) and self.has_common(range(ob.__coordinates__[1],ob.__coordinates__[1]+ob.__size__[1]+1),range(coordinates[1],coordinates[1]+size[1]+1)):
    #             return False
    #     return True
    #
    # def add_object(self,object):
    #     if self.is_available(object.__coordinates__,object.__is_structure__,object.__size__):
    #         self.__Objects__+=[object]

