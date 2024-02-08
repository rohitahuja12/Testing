import unittest

class PArrayFluoro(unittest.TestCase):

    def test_produce_intensity_list(self):
        images = []
        wells = []

        result = produceIntensityList(wells, images)
        # assert result stuff here


if __name__ == "__main__":
    unittest.main()
