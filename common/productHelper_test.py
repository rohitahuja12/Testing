import unittest
import sys
sys.path.insert(0, './common')
from common.productHelper import getAnalyteSpotMap, getFeatureFromPath, parseKitFeatures

class TestProductToolKit(unittest.TestCase):

    def test_kitJsonToFeatureGraph(self):
        fg = parseKitFeatures(kitJson)

        feature,x,y = getFeatureFromPath(fg, ['A1','microArray','IL-1alpha_1_3'])
        assert (x,y) == (9850, 112370)

    def test_canGetFeatureNames(self):
        fg = parseKitFeatures(kitJson)

        featNames = list(fg.features.keys())
        assert featNames[0] == 'A1'
        assert featNames[1] == 'A2'

kitJson = """
{
	"productName": "V2_Inflammatory_Kit_12P_061622",
	"productSchemaVersion": 1,
	"features": {
		"A1": {
			"x": 9550,
			"y": 111770,
			"features": {
				"microArray": { "$ref": "#/relativeFeatures/microArray" }
			}
		},
		"A2": {
			"x": 9550,
			"y": 102770,
			"features": {
				"microArray": { "$ref": "#/relativeFeatures/microArray" }
			}
		}
	},
	"relativeFeatures": {
		"microArray": {
			"x": 0,
			"y": 0,
			"features": {
				"POS_1_1": {
                    "attrs": {
                        "row": 1,
                        "col": 1,
                        "anaylte": "POS"
                    },
					"x": 0,
					"y": 600
				},
				"BLANK_1_2": {
                    "attrs": {
                        "row": 1,
                        "col": 2,
                        "analyte": "BLANK"
                    },
					"x": 150,
					"y": 600
				},
				"IL-1alpha_1_3": {
                    "attrs": {
                        "row": 1,
                        "col": 3,
                        "analyte": "IL-1alpha"
                    },
					"x": 300,
					"y": 600
				}
			}
		}
	}
}
"""

if __name__ == '__main__':
    unittest.main()
