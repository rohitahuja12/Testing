import unittest
import sys

sys.path.insert(0, './common')
sys.path.insert(0, './analyzer/src')
from pArrayFluoro_lib import *
import log

logger=log.getLogger('analyzer.src.protocols.pArrayFluoro_lib_test')
class TestPArrayFluoro_lib(unittest.TestCase):

    def test_mark_outliers(self):
        print("Mark outliers...")
        #1 outlier
        a1 = {"intensity":50000}
        a2 = {"intensity":50100}
        a3 = {"intensity":30000}
        input1 = [a1,a2,a3]

        r1 = {"intensity":50000, "outlier":0}
        r2 = {"intensity":50100, "outlier":0}
        r3 = {"intensity":30000, "outlier":1}
        expectedOutput1 = [r1,r2,r3]

        result1 = markOutliers(input1)
        print(result1)
        assert (result1 == expectedOutput1)

        a3 = {"intensity":50200}
        input2 = [a1,a2,a3]
        r3 = {"intensity":50200, "outlier":0}
        expectedOutput2 = [r1,r2,r3]

        result2 = markOutliers(input2)
        print(result2)
        assert (result2 == expectedOutput2)

        input3 = [a1,a2]
        result3 = markOutliers(input3)
        assert (result3 == input3)

    def test_replaceSpotOutliersWithinEachWell(self):
        
        spots = [
            # six spots in A1, 3 xs and 3 ys
            {
                "wellRow": "A",
                "wellColumn": "1",
                "analyte": "x",
                "intensity": 1
            },{
                "wellRow": "A",
                "wellColumn": "1",
                "analyte": "x",
                "intensity": 5
            },{
                "wellRow": "A",
                "wellColumn": "1",
                "analyte": "x",
                "intensity": 6
            },{
                "wellRow": "A",
                "wellColumn": "1",
                "analyte": "y",
                "intensity": 3
            },{
                "wellRow": "A",
                "wellColumn": "1",
                "analyte": "y",
                "intensity": 9
            },{
                "wellRow": "A",
                "wellColumn": "1",
                "analyte": "y",
                "intensity": 11
            },
            # three spots in B1
            {
                "wellRow": "B",
                "wellColumn": "1",
                "analyte": "x",
                "intensity": 7
            },{
                "wellRow": "B",
                "wellColumn": "1",
                "analyte": "x",
                "intensity": 6
            },{
                "wellRow": "B",
                "wellColumn": "1",
                "analyte": "x",
                "intensity": 7
            }
        ]

        res = transformSpots(
            spots,
            lambda ss: [ss[0]],
            lambda s: f"{s['wellRow']}{s['wellColumn']}{s['analyte']}"
        )

        logger.info(f'Result of transform: {res}')

        assert(len(res) == 3)

        #ax = next(x for x in res if x['wellRow']=="A" and x['wellColumn']=="1" and x['analyte']=="x")
        #ay = next(x for x in res if x['wellRow']=="A" and x['wellColumn']=="1" and x['analyte']=="y")
        #bx = next(x for x in res if x['wellRow']=="B" and x['wellColumn']=="1" and x['analyte']=="x")

        assert(res[0]['intensity'] == 1)
        assert(res[1]['intensity'] == 3)
        assert(res[2]['intensity'] == 7)

    # def test_addKnownConcentration(self):
        
        # init = {
            # "IFN-gamma": 2000,
            # "IL-10": 600
        # }
        # dilFactor = 3

        # spot = { "wellType": "blank", "analyte": "x" }
        # res = addKnownConcentration(spot, init, dilFactor)
        # assert(res['knownConcentration'] == 1*10**-20)

        # spot = { 
            # "wellType": "standard",
            # "wellLabel": "stnd3",
            # "analyte": "IL-10"
        # }
        # res = addKnownConcentration(spot, init, dilFactor)
        # assert(res['knownConcentration'] == 600/dilFactor/dilFactor)

        # # an unknown spot should come back unaffected
        # spot = { "wellType": "unknown", "analyte": "x" }
        # res = addKnownConcentration(spot, init, dilFactor)
        # assert(res)
        # assert(not res.get("knownConcentration", False))

        # # an POS spot should come back unaffected
        # spot = { "wellType": "standard", "analyte": "POS" }
        # res = addKnownConcentration(spot, init, dilFactor)
        # assert(res)
        # assert(not res.get("knownConcentration", False))

        # # a BLANK spot should come back unaffected
        # spot = { "wellType": "standard", "analyte": "BLANK" }
        # res = addKnownConcentration(spot, init, dilFactor)
        # assert(res)
        # assert(not res.get("knownConcentration", False))




if __name__ == "__main__":
    unittest.main()
