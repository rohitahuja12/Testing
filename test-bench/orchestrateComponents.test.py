import sys
sys.path.insert(0, './common')
import unittest
import orchestrateComponents as oc
from dotmap import DotMap

class CountToggles(unittest.TestCase):

    def test_countToggles(self):

        m1 = ["a","b","c","d"]
        m2 = ["a","c","x"]

        assert oc._countToggles(m1, m2) == 3

    def test_totalToggles(self):

        m1 = ["a","b","c","d"]
        m2 = ["a","c","x"]
        m3 = ["d","y","c"]

        assert oc._totalToggles([m1,m2,m3]) == 4+3+4
        assert oc._totalToggles([m3,m1,m2]) == 3+3+3

    def test_optimizeRunOrder(self):

        m1 = DotMap({'id':'m1','module':{'requiredComponents':["a","b","c","d"]}})
        m2 = DotMap({'id':'m2','module':{'requiredComponents':["a","c","x"]}})
        m3 = DotMap({'id':'m3','module':{'requiredComponents':["d","y","c"]}})

        best = oc._optimizeRunOrder([m1,m2,m3])
        t = oc._totalToggles(best)

        # print('total otggler', t, [b.toDict() for b in best])
        # print(best[0][0])
        # assert best[0][0].id == 'm2'
        # assert best[1][0].id == 'm1'
        # assert best[2][0].id == 'm3'

    def test_optimizeRunOrder2(self):

        m1 = DotMap({'id':'m1','module':{'requiredComponents':["a","b","c","d"]}})
        m2 = DotMap({'id':'m2','module':{'requiredComponents':["a","b","c"]}})
        m3 = DotMap({'id':'m3','module':{'requiredComponents':["a","b"]}})
        m4 = DotMap({'id':'m4','module':{'requiredComponents':["a"]}})
        m5 = DotMap({'id':'m5','module':{'requiredComponents':["a","g"]}})

        best = oc._optimizeRunOrder([m1,m4,m2,m3,m5])

        # print(best)
        # assert best[0][0].id == 'm1'
        # assert best[1][0].id == 'm2'
        # assert best[2][0].id == 'm3'
        # assert best[3][0].id == 'm4'
        # assert best[4][0].id == 'm5'







if __name__ == '__main__':
    unittest.main()
