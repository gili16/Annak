from OnTile import OnTile
from IMovable import IMoveable
import json


class Person(IMoveable):
    def __init__(self, coordinates):
        super().__init__(coordinates, "Person")


