import sys
sys.path.insert(0,"./analyzer/src")
sys.path.insert(0,"./common")
import artifactCodec
import curveFitter
import cv2
import json
import numpy as np
import random

codec = artifactCodec.ArtifactCodec()

def createArrayTestImages(product_parameters:dict, other_parameters:dict):

    scanImageHeightUm = other_parameters['scanImageHeightUm']
    scanImageWidthUm = other_parameters['scanImageWidthUm']
    scanImageHeightPx = other_parameters['scanImageHeightPx']
    scanImageWidthPx = other_parameters['scanImageWidthPx']

    umPerPxX = scanImageWidthUm / scanImageWidthPx
    umPerPxY = scanImageHeightUm / scanImageHeightPx

    analyteDict = other_parameters['analytes']
    dilutionFactor = other_parameters['dilutionFactor']
    backgroundIntensity = other_parameters['backgroundParameters']['backgroundIntensity']
    backgroundIntensityVariationFactor = other_parameters['backgroundParameters']['backgroundIntensityVariationFactor']
    dilutionIndexBackgroundMultiplierDict = other_parameters['backgroundParameters']['dilutionMultipliers']

    arrayShiftXUm = other_parameters['plateNoiseParameters']['arrayShiftXUm']
    arrayShiftYUm = other_parameters['plateNoiseParameters']['arrayShiftYUm']

    arrayShiftXPx = int(arrayShiftXUm / umPerPxX)
    arrayShiftYPx = int(arrayShiftYUm / umPerPxY)

    spotJitterFactor = other_parameters['plateNoiseParameters']['spotJitterFactor']

    posLabel = other_parameters['positiveControls']['analyteLabel']
    posIntensity = other_parameters['positiveControls']['absoluteIntensity']
    posIntensityVariationFactor = other_parameters['positiveControls']['positiveControlIntensityVariationFactor']
    spotDiameterUm = other_parameters['spotDiameterUm']
    spotDiameterPx = int(spotDiameterUm / umPerPxX)

    blockPointAnalyteDict = product_parameters['blockPointAnalytes']
    distanceBetweenSpotsUm = product_parameters['distanceBetweenSpotsUm']
    distanceBetweenSpotsPx = int(distanceBetweenSpotsUm / umPerPxX)
    print('dist between spots px', distanceBetweenSpotsPx)
    wellTypeDict = other_parameters['wellTypes']

    blockColumns = [col for row,col in blockPointAnalyteDict.keys()]
    blockRows = [row for row,col in blockPointAnalyteDict.keys()]
    blockColumnCt = max(blockColumns) - min(blockColumns) + 1
    blockRowCt = max(blockRows) - min(blockRows) + 1

    print('um per px ', umPerPxX)
    print('block column ct', blockColumnCt)
    print('block row ct', blockRowCt)
    topLeftSpotXUm = int((scanImageWidthUm-((blockColumnCt-1)*distanceBetweenSpotsUm))/2)
    topLeftSpotYUm = int((scanImageHeightUm-((blockRowCt-1)*distanceBetweenSpotsUm))/2)
    print('topleftspotx', topLeftSpotXUm)
    print('topleftspoty', topLeftSpotYUm)
    topLeftSpotXPx = int(topLeftSpotXUm / umPerPxX)
    topLeftSpotYPx = int(topLeftSpotYUm / umPerPxY)
    print('topleftspotpxx', topLeftSpotXPx)
    print('topleftspotpxy', topLeftSpotYPx)


    #print(analyteDict)
    # print(dilutionIndexBackgroundMultiplierDict)

    #get scan document to create data from
    #get product info from scan
    #for each scan well, create an image based on the data from the scan (std, unk, etc,


    def convertPointToCoords(pt):
        x,y = pt
        spacing = distanceBetweenSpotsPx
        return ( ((x-1)*spacing)+topLeftSpotXPx, ((y-1)*spacing)+topLeftSpotYPx )

    def offset(aPoint, arrayOffsetXPx, arrayOffsetYPx):
        x,y = aPoint
        return (int(x+arrayOffsetXPx), int(y+arrayOffsetYPx))

    def jitter(aPoint, jitterFactor):
        jitterDistanceX = random.uniform(1-jitterFactor, 1+jitterFactor)
        jitterDistanceY = random.uniform(1-jitterFactor, 1+jitterFactor)
        jitteredPoint = (int(aPoint[0]*jitterDistanceX),
                         int(aPoint[1]*jitterDistanceY) )
        return jitteredPoint

    wellImages = []

    for well, wellType in wellTypeDict.items(): #this will come from the scan
        #generate the well image data with a given background
        lowValue = backgroundIntensity - (backgroundIntensity * backgroundIntensityVariationFactor)
        highValue = backgroundIntensity + (backgroundIntensity * backgroundIntensityVariationFactor)
        wellData = np.random.uniform(
            low=lowValue, 
            high=highValue, 
            size=(scanImageWidthPx,scanImageHeightPx))

        #modify the background if so indicated by the dilution multiplier
        if wellType.startswith("stnd"):
            standardSeriesIndex = int(wellType[4:])
            if dilutionIndexBackgroundMultiplierDict:
                if str(standardSeriesIndex) in dilutionIndexBackgroundMultiplierDict:
                    wellData = wellData * dilutionIndexBackgroundMultiplierDict[str(standardSeriesIndex)]

        #for each well identified in the scan data + product
        if wellType != "blank":
            for blockPoint,analyte in blockPointAnalyteDict.items():
                if analyte in analyteDict:
                    analyteParamsDict = analyteDict[analyte]
                    stndParamsDict = analyteParamsDict["standardParameters"]
                    unkParamsDict = analyteParamsDict["unknownParameters"]
                    fitType = stndParamsDict["fitType"]
                    initialConcentration = stndParamsDict["initialConcentration"]

                    if wellType.startswith("stnd"):
                        targetConcentration = initialConcentration / (dilutionFactor**(standardSeriesIndex-1))
                        randomFactor = stndParamsDict["wellReplicateIntensityVariationFactor"]
                    else: #is an unknown
                        targetConcentration = unkParamsDict["targetConcentration"]
                        randomFactor = unkParamsDict["wellReplicateIntensityVariationFactor"]

                    cpd = stndParamsDict["curveParameters"]
                    if fitType == "4PL":
                        calculatedIntensity = curveFitter.logistic4( targetConcentration,
                                                                cpd["a"],
                                                                cpd["b"],
                                                                cpd["c"],
                                                                cpd["d"])
                    else:
                        #change this to logistic5 after merge
                        calculatedIntensity = curveFitter.logistic4( targetConcentration,
                                                                 cpd["a"],
                                                                 cpd["b"],
                                                                 cpd["c"],
                                                                 cpd["d"])

                    randomizedIntensity = calculatedIntensity * random.uniform(1-randomFactor, 1+randomFactor)
                    aPoint = convertPointToCoords((blockPoint[1],blockPoint[0]))
                    jitteredPoint = jitter(
                        aPoint, 
                        spotJitterFactor)
                    offsetJitteredPoint = offset(jitteredPoint, arrayShiftXPx, arrayShiftYPx)
                    # print(aPoint,jitteredPoint)
                    cv2.circle(wellData,offsetJitteredPoint,spotDiameterPx//2,randomizedIntensity,-1)

        #add the positive control spot to every well
        for blockPoint, analyte in blockPointAnalyteDict.items():
            if analyte == posLabel:
                randomizedIntensity = posIntensity * random.uniform(1-posIntensityVariationFactor, 1+posIntensityVariationFactor)
                aPoint = convertPointToCoords(blockPoint) #necessary for current test harnass
                jitteredPoint = jitter(aPoint, spotJitterFactor)
                offsetJitteredPoint = offset(jitteredPoint, arrayShiftXPx, arrayShiftYPx)
                cv2.circle(wellData,offsetJitteredPoint,spotDiameterPx//2,randomizedIntensity,-1)

        #save well image
        wellImages.append(wellData)

    return wellImages
