

class OnTile:
    def __init__(self,coordinates,type,size,is_structure):
        self.__coordinates__=coordinates
        self.__type__=type
        self.__size__=size
        self.__is_structure__=is_structure

    def move(self,coordinates):
        self.__coordinates__=coordinates

