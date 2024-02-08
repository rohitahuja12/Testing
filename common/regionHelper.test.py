import os
os.environ["COMPONENT_CLASS"] = "unittest"
import unittest
from regionHelper import *

# isolations of relevant parts of product and scan defs
productBody = {
    "features": [{
        "key": ["Well","A","12"],
        "region": [
            {"point":{"type":"extent","x":-10000,"y":-10000,"z":0}},
            {"point":{"x":-20000,"y":-12000}},
        ]
    },{
        "key": ["Well","A","11"],
        "region": [
            {"point":{"x":-50000,"y":-60000}},
            {"point":{"x":-23000,"y":-12300}},
        ]
    },{
        "key": ["Wells"],
        "region": [
            {"feature": ["Well","A","12"]},
            {"feature": ["Well","A","11"]}
        ]
    }]
}
scanArgs = { 
    "images": [{
        "region": [{"feature": ["Well","A","12"]}]
    }]
}



class TestRegionHelper(unittest.TestCase):

    def test_regions(self):

        getPoints = regions(productBody['features'])
        res = getPoints(scanArgs['images'][0]['region'])
        assert len(res)==2

    def test_regionsNested(self):

        getPoints = regions(productBody['features'])
        res = getPoints([{"feature": ["Wells"]}])
        assert len(res)==4

    def test_regionsUnnamed(self):

        getPoints = regions(productBody['features'])
        res = getPoints([{"point": {"x":1000,"y":1000}}])
        assert res[0].x == 1000




if __name__ == '__main__':
    unittest.main()
