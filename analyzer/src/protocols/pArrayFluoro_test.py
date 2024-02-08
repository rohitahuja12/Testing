import sys

import numpy as np

sys.path.insert(0, './common')
sys.path.insert(0, './common/mock_image_creator')
sys.path.insert(0, './common/spot_intensity_detector')
sys.path.insert(0, './analyzer/src')

import unittest
import log
import json
import asyncio
from unittest import IsolatedAsyncioTestCase

from imageLib import loadImage
from curveFitter import logistic4

import artifactCodec
from regionHelper import regions
from pArrayFluoro import getIntensities
from pArrayFluoro import getImageDetails

from productHelper import getAnalyteSpotMap

from detector import *

import imageGenerator as imgen

#from detector import *

#sys.path.insert(0, './analyzer/src')
#from pArrayFluoro import *

logger=log.getLogger('analyzer.src.protocols.pArrayFluoro_test')
codec = artifactCodec.ArtifactCodec()

#class PArrayFluoro(unittest.TestCase):
class PArrayFluoro(IsolatedAsyncioTestCase):
    product_settings = {
        "blockPointAnalytes": {
            (1,1):"POS",
            (1,3):"IL-1a",
            # (1,4):"IL-1b",
            # (1,5):"IL-2",
            # (1,6):"IL-4",
            (6,6):"IL-6",
            (3,3):"IL-1a",
            (4,5):"IL-1a",
            (7,4):"IL-6",
            (5,2):"IL-6"
        },
        "distanceBetweenSpotsUm": 500
    }
    other_settings = {
        "wellTypes": {
            "A1":"stnd1",
            "A2":"stnd2"
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
        "scanImageHeightPx": 4400,
        "scanImageWidthPx": 4400,
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

    async def test_getIntensities(self):
        logger.info("Running test_getIntensities")

        #detector method
        newProductFile = open('./analyzer/testData/product_6-6-23.json')
        newProductJson = json.load(newProductFile)
        print(type(newProductJson))
        features = newProductJson['relativeFeatures']['microArray']['features']
        newProductFile.close()

        testImage = loadImage("./analyzer/testData/A1.tif")
        imgArray = np.array(testImage)

        #detector method
        imgArray2 = imgen.createArrayTestImages(self.product_settings, self.other_settings)
        print(f"Number of images: {len(imgArray2)}")

        productFile = open('./analyzer/testData/product.json')
        productJson = json.load(productFile)
        productFile.close()

        imageMetadataFile = open('./analyzer/testData/imageMetadata.json')
        imageMetadataJson = json.load(imageMetadataFile)
        imageMetadataFile.close()
        print(imageMetadataJson)

        well = {'column': '1', 'knownConcentration': 1000, 'label': 'stnd1', 'replicateIndex': 1, 'row': 'A', 'type': 'standard'}

        well2 = {'column': '1', 'knownConcentration': 1000, 'label': 'stnd1', 'replicateIndex': 1, 'row': 'A', 'type': 'standard'}
        well3 = {'column': '2', 'knownConcentration': 333.333, 'label': 'stnd2', 'replicateIndex': 1, 'row': 'A', 'type': 'standard'}

        experimentWells = [well2, well3]

        #detector method
        print("******** SCAN IMAGE METADATA")
        imageMetadataList = getImageDetails(imageMetadataJson,experimentWells)
        print(imageMetadataList)

        featureToPoints = lambda k: regions(productJson['features'])([{"feature":k}])

        res = featureToPoints(["Well", well['row'], well['column']])
        well.update({'image':imgArray})

        well2.update({'image':imgArray2[0]})
        well3.update({'image':imgArray2[1]})

        wells = [well]
        wells2 = [well2,well3]

        print("*** WELL")
        print(well)
        print()
        print("*** FEATURE TO POINTS")
        print(featureToPoints(["Well", well['row'], well['column']])[0].toDict() )
        print(featureToPoints(["Well", well['row'], well['column']])[1].toDict() )
        print(featureToPoints(["Well", well['row'], well['column']])[2].toDict() )
        print()

        async def someFunc(*args):
            return None

        async def addSpotIntensities(well):
            return {
                **well,
                "spots": await getIntensities(
                    well,
                    featureToPoints(["Well", well['row'], well['column']]),
                    someFunc)
            }

        resultList = await asyncio.gather(*[
            addSpotIntensities(w) for w in wells
        ])

        # REPLACE addSpotIntensities
        spotDiameterPx = 200 #from product
        spotDistancePx = 500 #from product
        signalIntensityAlgorithm = "mean-threshold"
        #run detector and get the intensities
        resIntensities, resStats, annotatedImages = detect_intensities(imgArray2,
                                                                       imageMetadataList,
                                                                       { 'spotDiameterPx':spotDiameterPx,
                                                                         'spotDistancePx':spotDistancePx,
                                                                         'signalIntensityAlgorithm':signalIntensityAlgorithm}
                                                                       )

        print("*** Dector intensitites")
        print(resIntensities)
        print("")

        for w in wells2:
            wellRow = w['row']
            wellColumn = w['column']
            wellLabel = wellRow+wellColumn
            spotIntensityList = []
            for s in resIntensities:
                if s.well == wellLabel:
                    spotDict = {}
                    spotDict['analyte']=s.analyte
                    spotDict['column']=s.column
                    spotDict['row']=s.row
                    spotDict['type']="spot"
                    spotDict['intensity']=s.intensity
                    #spotDict['x']=?
                    #spotDict['y']=?
                    spotIntensityList.append(spotDict)
            w['spots']=spotIntensityList

        print("")
        print("*** RESULT LIST (after addSpotIntensities)")
        print(resultList)
        print("")
        print("*** RESULT LIST (after detector)")
        print(wells2)
        print("")

        spots = resultList[0]['spots']
        #print(spots)

        #compare spot intensities to stored json file
        resultFile = open('./analyzer/testData/spotIntensitiesResults.json')
        resultJson = json.load(resultFile)
        resultFile.close()
        for r in resultJson:
            r.update({"intensity":np.float32(r['intensity'])})
        assert spots==resultJson, logger.error("Calculated spot intensities not equal to stored spot intensities.")



if __name__ == "__main__":
    unittest.main()