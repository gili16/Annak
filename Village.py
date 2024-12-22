# from OnTile import OnTile
import json
from Structure import Structure
class Village(Structure):
    def __init__(self,coordinates):
        f = open('./configuration.json')
        sizes = json.load(f)["Sizes"]
        super.__init__(coordinates,"Village",sizes["Village"],True)
        # self.__capacity__=[0,0,0,0,0]
