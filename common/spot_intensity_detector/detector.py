import numpy as np
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List
from typing import Tuple

import cv2
import math
import log

import imageLib

logger=log.getLogger('common.spot_intensity_detector.detector')

@dataclass_json
@dataclass
class SpotAcqDetails:
    analyte: str
    row: int
    column: int
    x_px: int
    y_px: int

@dataclass_json
@dataclass
class ImageAcqDetails:
    time: str
    fovSizeXUm: int
    fovSizeYUm: int
    zStagePositionUm: int
    xStagePositionUm: int
    yStagePositionUm: int
    imageName: str
    spots: List[SpotAcqDetails]

@dataclass_json
@dataclass
class SpotIntensity:
    image_name: str
    analyte: str
    row: int
    column: int
    intensity: float

@dataclass_json
@dataclass
class RoiMetadata:
    parentImage: str
    label: str
    row: int
    column: int
    center: Tuple[int,int]
    upperLeft: Tuple[int,int]
    lowerRight: Tuple[int,int]
@dataclass_json
@dataclass
class RoiStatistics:
    well: str
    analyte: str
    row: int
    column: int
    upperLeftPoint: Tuple[int,int]
    lowerRightPoint: Tuple[int,int]
    totalMean: float
    totalMedian: float
    backgroundMean: float
    backgroundMedian: float
    signalMean: float
    signalMedian: float
    totalPixels: int
    signalPixels: int
    backgroundPixels: int
    calculatedIntensity: float

@dataclass_json
@dataclass
class RoiIntensity:
    well: str
    wellRow: str
    wellColumn: str
    analyte: str
    row: int
    column: int
    intensity: float

def create_roi_image(image, roi):
    return image[
        roi.upperLeft[1] : roi.lowerRight[1],
        roi.upperLeft[0] : roi.lowerRight[0]
    ]

def calculateFontParams(img, fontScale = 1, thicknessScale = 5e-3):
    h, w, _ = img.shape
    fontScale = min(w, h) / 2000
    thickness = int(min(w, h) / 500)
    return fontScale, thickness

def createAnnotatedWellImage(image, rois, wellName, spotDiameter, signalIntensityAlgorithm):
        #annotate image
        imLogged = np.log2(image)
        im = imageLib.imageToColorImage(imLogged)
        im = imageLib.invert(im)
        im = cv2.applyColorMap(im,cv2.COLORMAP_JET)

        w,h, _ = im.shape
        aspectRatio = w/h
        targetSize = 800
        im = cv2.resize(im, (targetSize, int(targetSize*aspectRatio)) )
        scaleFactor = targetSize/w

        aColor = (225,225,0)
        fontScale, thickness = calculateFontParams(im)
        fontFace = cv2.FONT_HERSHEY_SIMPLEX
        wellScaleFactor = 3
        roiTextSize = cv2.getTextSize(text="X", fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=fontScale, thickness=thickness)
        wellTextSize = cv2.getTextSize(text="X", fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=wellScaleFactor*fontScale, thickness=thickness)
        cv2.putText(im,wellName,(wellTextSize[0][0],10+wellTextSize[0][1]),fontFace,wellScaleFactor*fontScale,aColor,2*thickness,cv2.LINE_AA)
        for r in rois:
            scaledUpperLeft = tuple((scaleFactor*np.array(r.upperLeft)).astype(int))
            scaledLowerRight = tuple((scaleFactor*np.array(r.lowerRight)).astype(int))
            scaledCenter = tuple((scaleFactor*np.array(r.center)).astype(int))
            cv2.rectangle(im, tuple((scaleFactor*np.array(r.upperLeft)).astype(int)),tuple((scaleFactor*np.array(r.lowerRight)).astype(int)), aColor, 1 )
            cv2.putText(im,
                        f"{r.label} ({r.row},{r.column})",
                        (scaledUpperLeft[0]+roiTextSize[0][0],scaledUpperLeft[1]+int(1.5*roiTextSize[0][1])),
                        fontFace,
                        fontScale,
                        aColor,
                        1,
                        cv2.LINE_AA)

            #add a circle for circle based intensity calculations
            if signalIntensityAlgorithm == "circle-threshold":
                roiWidth = scaledLowerRight[0]-scaledUpperLeft[0]
                radius = int(.75*roiWidth/2)
                cv2.circle(im,
                           scaledCenter,
                           radius,
                           aColor,
                           1)

        return im

def detect_intensities(
        images: List[np.ndarray],
        image_metadata: List[ImageAcqDetails], 
        params = None
    ) -> Tuple[ List[RoiIntensity], List[RoiStatistics], List[np.ndarray] ]:

    #some product data we'll need to inject
    spotDiameter = params['spotDiameterPx']
    spotDistance = params['spotDistancePx']
    halfSpotDistance = int(spotDistance/2)
    signalIntensityAlgorithm = params['signalIntensityAlgorithm']

    resultIntensities = []
    resultStatistics = []
    resultAnnotatedImages = {}


    def get_intensity_statistics_circle_threshold(roiImage):

        w,h = np.shape(roiImage)
        centerX = int(w/2)
        centerY = int(h/2)
        radius = int((.75*w)/2)
        Y,X = np.ogrid[:w,:h]
        distance = np.sqrt((X-centerX)**2 + (Y-centerY)**2)
        mask = distance <= radius
        bg = roiImage[~mask]
        bgMean = np.mean(bg)
        countInsideCircle = np.sum(mask == 1)
        countOutsideCircle = np.sum(mask == 0)
        std = np.std(bg)
        threshold = bgMean+(2*std)
        signalSum = np.sum(roiImg[roiImage>threshold])
        signalMean = np.mean(roiImage[roiImage>threshold])

        result = { "intensity":signalSum, "threshold":threshold }
        return result

    def get_intensity_statistics_mean_threshold(roiImage, roiMetadata):

        mean = np.mean(roiImage)
        median = np.median(roiImage)

        signalPixelCriteria = roiImage > mean
        signalPixels = np.sum(signalPixelCriteria)
        signalMean = np.mean(roiImage, where=roiImage>mean)
        signalMedian = np.median(roiImage[signalPixelCriteria])

        backgroundPixelCriteria = roiImage <= mean
        backgroundPixels= np.sum(backgroundPixelCriteria)
        backgroundMean = np.mean(roiImage, where=roiImage<=mean)
        backgroundMedian = np.median(roiImage[backgroundPixelCriteria])

        totalPixels = roiImage.size

        res = signalMean - backgroundMean

        wellRow = roiMetadata.parentImage[0]
        wellColumn = roiMetadata.parentImage[1:] #was int casted

        intensityResult = RoiIntensity(
            well=roiMetadata.parentImage,
            wellRow=wellRow,
            wellColumn=wellColumn,
            analyte=roiMetadata.label,
            row=roiMetadata.row,
            column=roiMetadata.column,
            intensity=res
        )

        statisticsResult = RoiStatistics(
            well=roiMetadata.parentImage,
            analyte=roiMetadata.label,
            row=roiMetadata.row,
            column=roiMetadata.column,
            upperLeftPoint=roiMetadata.upperLeft,
            lowerRightPoint=roiMetadata.lowerRight,
            totalMean=mean,
            totalMedian=median,
            backgroundMean=backgroundMean,
            backgroundMedian=backgroundMedian,
            signalMean=signalMean,
            signalMedian=signalMedian,
            totalPixels=totalPixels,
            signalPixels=int(signalPixels),
            backgroundPixels=int(backgroundPixels),
            calculatedIntensity=res
        )

        return intensityResult, statisticsResult
    def get_intensity_statistics_mean_threshold2(roiImage):
        mean = np.mean(roiImage)
        signalMean = np.mean(roiImage, where=roiImage>mean)
        backgroundMean = np.mean(roiImage, where=roiImage<=mean)
        res = signalMean - backgroundMean
        result = { "intensity": res, "threshold":mean}
        return result

    def get_intensity_statistics(roiImage, roiMetadata, signalIntensityAlgorithm):

        #default calculations for every analysis
        mean = np.mean(roiImage)
        median = np.median(roiImage)
        totalPixels = roiImage.size
        wellRow = roiMetadata.parentImage[0]
        wellColumn = roiMetadata.parentImage[1:] #was int casted

        #switchable analysis results
        intensityThresholdDict = {}
        match signalIntensityAlgorithm:
            case "mean-threshold":
                intensityThresholdDict = get_intensity_statistics_mean_threshold2(roiImage)
            case "circle-threshold":
                intensityThresholdDict = get_intensity_statistics_circle_threshold(roiImage)
            case _:
                intensityThresholdDict = get_intensity_statistics_mean_threshold2(roiImage)

        #calculate analysis specific stats based on return of intensity and threshold
        intensity = intensityThresholdDict["intensity"]
        threshold = intensityThresholdDict["threshold"]

        intensityResult = RoiIntensity(
            well=roiMetadata.parentImage,
            wellRow=wellRow,
            wellColumn=wellColumn,
            analyte=roiMetadata.label,
            row=roiMetadata.row,
            column=roiMetadata.column,
            intensity=intensity
        )

        backgroundMean = np.mean(roiImg[roiImage<=threshold])
        backgroundMedian = np.mean(roiImg[roiImage<=threshold])
        signalMean = np.mean(roiImage[roiImage>threshold])
        signalMedian = np.median(roiImage[roiImage>threshold])
        signalPixelCriteria = roiImage > threshold
        signalPixels = np.sum(signalPixelCriteria)
        backgroundPixelCriteria = roiImage <= threshold
        backgroundPixels = np.sum(backgroundPixelCriteria)

        statisticsResult = RoiStatistics(
            well=roiMetadata.parentImage,
            analyte=roiMetadata.label,
            row=roiMetadata.row,
            column=roiMetadata.column,
            upperLeftPoint=roiMetadata.upperLeft,
            lowerRightPoint=roiMetadata.lowerRight,
            totalMean=mean,
            totalMedian=median,
            backgroundMean=backgroundMean,
            backgroundMedian=backgroundMedian,
            signalMean=signalMean,
            signalMedian=signalMedian,
            totalPixels=totalPixels,
            signalPixels=int(signalPixels),
            backgroundPixels=int(backgroundPixels),
            calculatedIntensity=intensity
        )

        return intensityResult, statisticsResult


    for image, metadata in zip(images, image_metadata):
        #find spots and write out summary images
        #get the parameters from function input and/or product data
        #find expected positive control coords
        #calculate intensities and statistics

        wellMean = np.mean(image)
        wellMedian = np.median(image)

        foundSpotDict = imageLib.findSpots(image, spotDiameter, spotDiameter, wellMedian)
        expectedSpots = metadata.spots

        #find positive control point in expected spot point cloud
        posControlPoint = next(s for s in expectedSpots
                          if s.analyte == "POS" )

        posX = int(posControlPoint.x_px)
        posY = int(posControlPoint.y_px)

        posRow = int(posControlPoint.row)
        posCol = int(posControlPoint.column)

        origin = (0,0)
        spotNearestPosControl = min(
            foundSpotDict,
            key=lambda s: pow(s['x']-posControlPoint.x_px, 2)+pow(s['y']-posControlPoint.y_px, 2))
            #key=lambda s: pow(s['x']-origin[0], 2)+pow(s['y']-origin[1], 2))

        foundPosX = spotNearestPosControl['x'];
        foundPosY = spotNearestPosControl['y'];

        #adjust POS control point if not at 0,0 block coordinate
        foundPosX = foundPosX - (spotDistance * (posCol-1))
        foundPosY = foundPosY - (spotDistance * (posRow-1))

        #create rois from detected spots
        roiDescriptions = []
        for e in expectedSpots:
            anl = e.analyte
            x = foundPosX + ((int(e.column)-1) * spotDistance)
            y = foundPosY + ((int(e.row)-1) * spotDistance)
            roiDescriptions.append( RoiMetadata(
                            parentImage=metadata.imageName,
                            label=anl,
                            row=int(e.row),
                            column=int(e.column),
                            center=(int(x),int(y)),
                            upperLeft=(int(x-halfSpotDistance),int(y-halfSpotDistance)),
                            lowerRight=(int(x+halfSpotDistance),int(y+halfSpotDistance)),
                        )
            )

        #create validation images from rois
        annotatedImage = createAnnotatedWellImage(image,
                                                  roiDescriptions,
                                                  metadata.imageName,
                                                  spotDiameter,
                                                  signalIntensityAlgorithm)

        #create spot images from images and rois
        roiImages = [
            create_roi_image(image, roi)
            for roi in roiDescriptions
        ]

        #return the results of the roi processing
        statisticsList = []
        intensitiesList = []
        for roiImg, roi in zip(roiImages, roiDescriptions):
            intensity, statistics = get_intensity_statistics(roiImg, roi, signalIntensityAlgorithm)
            statisticsList.append(statistics)
            intensitiesList.append(intensity)

        #add the spot information for this well to the result set that will be returned
        resultIntensities.extend(intensitiesList)
        resultStatistics.extend(statisticsList)
        resultAnnotatedImages[metadata.imageName]=annotatedImage

    #return all_spot_intensities, all_spot_statistics
    return resultIntensities, resultStatistics, resultAnnotatedImages
