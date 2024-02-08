import sys
sys.path.insert(0,'.')
import unittest
import common.mock_image_creator.imageGenerator as imgen
import artifactCodec
codec = artifactCodec.ArtifactCodec()
from detector import *
from pprint import PrettyPrinter
print = PrettyPrinter().pprint
import dataclasses
import dataclasses_json
import csv
import json


class DetectorTest(unittest.TestCase):
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
            "A2":"stnd2",
            "A3":"stnd3",
            "A4":"stnd4",
            "A5":"stnd5",
            "A6":"stnd6",
            "A7":"stnd7",
            "A8":"stnd8",
            "A9":"stnd9",
            "A10":"stnd10",
            "A11":"stnd11",
            "A12":"blank"
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



    def test_detect_intensities(self):

        # in this dataset, px == microns for simplicity
        images = imgen.createArrayTestImages(self.product_settings, self.other_settings)

        #print(f"Number of images: {len(images)}")

        spot_dist = self.product_settings['distanceBetweenSpotsUm']
        im_width = self.other_settings['scanImageWidthUm']
        im_height = self.other_settings['scanImageHeightUm']
        x_start = ((im_width-6*spot_dist)/2)
        y_start = ((im_height-6*spot_dist)/2)

        image_metadata = [
            SpotAcqDetails(
                analyte=name,
                row=row,
                column=col,
                x_px=int(x_start+(col-1)*spot_dist),
                y_px=int(y_start+(row-1)*spot_dist)
            )
            for (row,col),name in self.product_settings['blockPointAnalytes'].items()
        ]

        details = [ImageAcqDetails(imageName="A1", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0),
                   ImageAcqDetails(imageName="A2", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0),
                   ImageAcqDetails(imageName="A3", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0),
                   ImageAcqDetails(imageName="A4", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0),
                   ImageAcqDetails(imageName="A5", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0),
                   ImageAcqDetails(imageName="A6", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0),
                   ImageAcqDetails(imageName="A7", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0),
                   ImageAcqDetails(imageName="A8", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0),
                   ImageAcqDetails(imageName="A9", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0),
                   ImageAcqDetails(imageName="A10", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0),
                   ImageAcqDetails(imageName="A11", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0),
                   ImageAcqDetails(imageName="A12", spots=image_metadata,time="",fovSizeYUm=0,fovSizeXUm=0,zStagePositionUm=0,xStagePositionUm=0,yStagePositionUm=0)]

        #print("*** INPUT TO DETECTOR, details")
        #print(details)
        #for d in details:
           #detailsDict = dataclasses.asdict(d)
           #detailsJson = json.dumps(detailsDict)
           #print(detailsJson)
        #print("")

        resIntensities, resStats, annotatedImages = detect_intensities(images,
                                                                       details,
                                                                       { 'spotDiameterPx':200,
                                                                        'spotDistancePx':500,
                                                                         'signalIntensityAlgorithm':"mean-threshold"})
        assert len(resStats) == 84
        assert len(resIntensities) == 84
        assert len(annotatedImages) == 12
        #csvResults = codec.dataclassObjectArrayToCsv(resStats)
        #for key,value in annotatedImages.items():
        #    cv2.imwrite(f"test-results/image-{key}.jpg",value)
        #with open("test-results/results.csv",'wb') as csvfile:
        #    csvfile.write(csvResults)



if __name__ == "__main__":
    unittest.main()
