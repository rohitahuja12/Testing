import sys
sys.path.insert(0,'.')
import unittest
import common.mock_image_creator.imageGenerator as imgen
import artifactCodec
codec = artifactCodec.ArtifactCodec()
from detector import *
from pprint import PrettyPrinter
print = PrettyPrinter().pprint

class DetectorTest(unittest.TestCase):
    product_settings = {
        "blockPointAnalytes": { 
            (1,1):"POS",
            (1,3):"IL-1a",
            # (1,4):"IL-1b",
            # (1,5):"IL-2",
            # (1,6):"IL-4",
            # (1,7):"IL-5",
            (3,3):"IL-6",
            (4,5):"IL-6",
            (2,1):"IL-1a",
            (7,4):"IL-1a",
            (5,2):"IL-1a",
            (1,7):"IL-1a"

        },
        "distanceBetweenSpotsUm": 500
    }
    other_settings = {
        "wellTypes": {
            "A1":"stnd1"
        },
        "analytes": {
            "IL-6": {
                "standardParameters": {
                    "initialConcentration": 1000,
                    "fitType": "4PL",
                    "curveParameters": {
                        "a": 1000,
                        "b": 1,
                        "c": 70,
                        "d": 90000
                    },
                    "wellReplicateIntensityVariationFactor": 0.1
                },
                "unknownParameters": {
                    "wellReplicateIntensityVariationFactor": 0.1,
                    "targetConcentration": 500
                }
            },
            "IL-1a": {
                "standardParameters": {
                    "initialConcentration" : 800,
                    "fitType" : "4PL",
                    "curveParameters": {
                        "a": 1200,
                        "b": 1,
                        "c": 80,
                        "d": 80000
                    },
                    "wellReplicateIntensityVariationFactor": 0.1
                },
                "unknownParameters": {
                    "wellReplicateIntensityVariationFactor": 0.1,
                    "targetConcentration": 500
                }
            }
        },
        "dilutionFactor": 3,
        "spotDiameterUm": 200,
        "scanImageHeightUm": 4400,
        "scanImageWidthUm": 4400,
        "scanImageHeightPx": 2200,
        "scanImageWidthPx": 2200,
        "backgroundParameters": {
            "backgroundIntensity" : 1100,
            "backgroundIntensityVariationFactor" : 0.5,
            "dilutionMultipliers" : { "1": 3, "2" : 2, "3": 2 }
        },
        "plateNoiseParameters": {
            "arrayShiftXUm": 0,
            "arrayShiftYUm": 0,
            "spotJitterFactor": 0.01
        },
        "positiveControls": {
            "analyteLabel": "POS",
            "absoluteIntensity" : 65000,
            "positiveControlIntensityVariationFactor": 0.05
        }
    }

    def test_something(self):

        images = imgen.createArrayTestImages(self.product_settings, self.other_settings)

        top_lefts = [(0,0)]
        bottom_rights = [(4400,4400)]
        spot_points = [
            (x*500+700,y*500+700,(x+1,y+1)) 
            for x in range(7)
            for y in range(7)
        ]
        roi_size = 500

        res = detect_intensities(images, top_lefts, bottom_rights, spot_points, roi_size)

        print(res)
        def get_spot_with_name(name):
            return lambda xs: next((x for x in xs if x[2] == name), None)

        assert 55000 < get_spot_with_name((1,1))(res)[-1] < 70000
        assert 0 < get_spot_with_name((1,3))(res)[-1] < 2000

        # for index, wellImage in enumerate(images):
            # im = codec.arrayToTiff(wellImage)
            # with open(f"test-out-{index+1}.tif",'wb') as f:
                # f.write(im)

            
            


if __name__ == "__main__":
    unittest.main()
