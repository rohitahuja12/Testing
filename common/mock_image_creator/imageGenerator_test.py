import unittest
import sys
sys.path.insert(0, './analyzer/src')
sys.path.insert(0, './common')
import imageGenerator as imGen
import artifactCodec
import cv2
#from pArrayFluoro_lib import *
codec = artifactCodec.ArtifactCodec()

class ImageGenerator(unittest.TestCase):

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
            "A1":"stnd1",
            "A2":"stnd2",
            "A3":"stnd3",
            "A4":"blank",
            "B1":"sample-123"
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
        "scanImageHeightPx": 1200,
        "scanImageWidthPx": 1200,
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

    def test_generateImage(self):

        res = imGen.createArrayTestImages(self.product_settings, self.other_settings)
        print(res[0])
        for index, wellImage in enumerate(res):
            im = codec.arrayToTiff(wellImage)
            with open(f"test-out-{index+1}.tif",'wb') as f:
                f.write(im)



if __name__ == "__main__":
    unittest.main()
