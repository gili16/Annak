# from OnTile import OnTile
import json
from Structure import Structure
class City(Structure):
    def __init__(self,coordinates):
        f = open('./configuration.json')
        sizes = json.load(f)["Sizes"]
        super.__init__(coordinates,"City")


