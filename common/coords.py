from dataclasses import dataclass, field
import copy
from typing import Dict

class CoordTriplet():
    x: int
    y: int
    z: int = 0
    dict: Dict = {}

    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    def to(self, dest):
        return minus(dest, self)

    @staticmethod
    def fromDict(d):
        res = CoordTriplet(d['x'], d['y'], d.get('z',0))
        res.dict = copy.deepcopy(d)
        return res

    def toDict(self):
        return {**self.dict, 'x': self.x, 'y': self.y, 'z': self.z}

    def toInt(self):
        res = copy.deepcopy(self)
        res.x = int(self.x)
        res.y = int(self.y)
        res.z = int(self.z)
        return res
    
    def __add__(self, other):
        res = copy.deepcopy(self)
        res.dict = {**res.dict, **other.dict}
        res.x = self.x + other.x
        res.y = self.y + other.y
        res.z = self.z + other.z
        return res

    def __sub__(self, other):
        res = copy.deepcopy(self)
        res.dict = {**res.dict, **other.dict}
        res.x = self.x - other.x
        res.y = self.y - other.y
        res.z = self.z - other.z
        return res

    def __mul__(self, other):
        res = copy.deepcopy(self)
        res.dict = {**res.dict, **other.dict}
        res.x = self.x * other.x
        res.y = self.y * other.y
        res.z = self.z * other.z
        return res

    def __truediv__(self, other):
        res = copy.deepcopy(self)
        res.dict = {**res.dict, **other.dict}
        res.x = self.x / other.x
        res.y = self.y / other.y
        res.z = self.z / other.z if other.z != 0 else 0
        return res

    def __floordiv__(self, other):
        res = copy.deepcopy(self)
        res.dict = {**res.dict, **other.dict}
        res.x = self.x // other.x
        res.y = self.y // other.y
        res.z = self.z // other.z if other.z != 0 else 0
        return res
    
    def __eq__(self, other):
        res = copy.deepcopy(self)
        res.dict = {**res.dict, **other.dict}
        res.x = self.x == other.x
        res.y = self.y == other.y
        res.z = self.z == other.z
        return res

class Point(CoordTriplet):
    pass

class Vect(CoordTriplet):
    pass

def minus(a: CoordTriplet, b: CoordTriplet) -> CoordTriplet:
    c = copy.deepcopy(a)
    c.x = a.x - b.x
    c.y = a.y - b.y
    c.z = a.z - b.z
    return c

def mult(a: CoordTriplet, b: CoordTriplet) -> CoordTriplet:
    c = copy.deepcopy(a)
    c.x = a.x * b.x
    c.y = a.y * b.y
    c.z = a.z * b.z
    return c

