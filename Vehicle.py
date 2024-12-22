
from IMovable import IMoveable

class Vehicle(IMoveable):
    def __init__(self,coordinates,type):
        self.__resources_matrix__=[0,0,0,0]
        self.__people__=[]
        super().__init__(coordinates,type)

    def remove_person(self,person):
        length=range(len(self.__people__))
        for i in length:
            if self.__people__[i].__coordinates__==person.__coordinates__:
                self.__people__.pop(i)
                break
