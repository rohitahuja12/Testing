import unittest
import sys
sys.path.insert(0, './common')
sys.path.insert(0, './analyzer/src')
from twist_corrector import *
import log

logger=log.getLogger('reader.svc_controller_stage.twist_corrector_test.py')
class TwistCorrectorTest(unittest.TestCase):

    def test_no_twist(self):
        twist = 0
        skew = 0
        (x,y) = (100,100)
        res = stageToTrue(x, y, twist, skew)
        assert res == (x,y)
        res = trueToStage(x, y, twist, skew)
        assert res == (x,y)

if __name__ == "__main__":
    unittest.main()
