import unittest
from coords import *

class CoordsMinus(unittest.TestCase):

    def runTest(self):

        feature1 = Point(-500,-500)
        cameraCenter = Point(10000,10000)

        res = minus(cameraCenter, feature1)
        assert res.x == 10000 - -500
        assert res.y == 10000 - -500
        assert res.z == 0

class CoordsMult(unittest.TestCase):

    def runTest(self):

        a = Point(-500,-500)
        b = CoordTriplet(100, 100, 100)
        res = mult(a, b)

        assert res.x == 100 * -500
        assert res.y == 100 * -500
        assert res.z == 0

class CoordsTo(unittest.TestCase):

    def runTest(self):

        feature1 = Point(-500,-500)
        cameraCenter = Point(10000,10000)

        res = feature1.to(cameraCenter)

        assert res.x == 10000 - -500
        assert res.y == 10000 - -500
        assert res.z == 0

class CoordsToFromDictRetainsOverloads(unittest.TestCase):

    def runTest(self):

        ptDict = {
            "name": "testName",
            "x": 1,
            "y": 2,
            "z": 3
        }
        pt = Point.fromDict(ptDict)
        pt2 = pt + Point(3,5,1)
        res = pt2.toDict()

        assert res['name'] == "testName"


if __name__ == "__main__":
    unittest.main()
