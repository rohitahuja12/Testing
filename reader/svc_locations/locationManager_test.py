import math
import unittest
from locationManager import *

class LocationManagerTest(unittest.TestCase):

    def testKitToStage(self):
        result = kitToStage(
            kitPoint=(0,0),
            kitToAdapterRotation=0,
            kitToAdapterOffset=(0,0),
            kitToAdapterInvert=(False,False),
            adapterToStageRotation=0,
            adapterToStageOffset=(0,0),
            adapterToStageInvert=(False,False),
            calibrationOffset=(0,0))
        assert result == (0,0)
    
        result = kitToStage(
            kitPoint=(1,5),
            kitToAdapterRotation=90,
            kitToAdapterOffset=(0,0),
            kitToAdapterInvert=(False,False),
            adapterToStageRotation=0,
            adapterToStageOffset=(0,0),
            adapterToStageInvert=(True,False),
            calibrationOffset=(0,0))
        assert result == (5,1)

        result = kitToStage(
            kitPoint=(1,5),
            kitToAdapterRotation=90,
            kitToAdapterOffset=(0,0),
            kitToAdapterInvert=(False,False),
            adapterToStageRotation=0,
            adapterToStageOffset=(10,10),
            adapterToStageInvert=(True,False),
            calibrationOffset=(0,0))
        assert result == (15,11)


if __name__ == "__main__":
    unittest.main()
