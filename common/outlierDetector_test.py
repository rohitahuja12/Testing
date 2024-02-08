import unittest
from common.outlierDetector import *

class TestOutlierDetector(unittest.TestCase):

    def test_outlierDetector(self):
        data1 = [22, 28, 1000]
        res1 = dixon_test(data1)

        data2 = [22, 1003, 1000]
        res2 = dixon_test(data2)

        data3 = [1012, 1003, 1000]
        res3 = dixon_test(data3)

        print(f"Result: {res1}")
        print(f"Result: {res2}")
        print(f"Result: {res3}")

        assert (len(res1)== 1 and res1[0] == 1000)
        assert (len(res2) == 1 and res2[0] == 22 )
        assert (len(res3) == 0 )


if __name__ == '__main__':
    unittest.main()