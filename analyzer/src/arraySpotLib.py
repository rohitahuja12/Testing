import imageLib
import cv2
import numpy as np
import operator

def findSpotPoint(image, points, windowLength, maxDetectionDistance, thresholdFactor):

    (pX,pY) = points

    startRow = pY-int(windowLength/2)
    endRow = pY+int(windowLength/2)
    startCol = pX-int(windowLength/2)
    endCol = pX+int(windowLength/2)
    sub = image[int(startRow):int(endRow),int(startCol):int(endCol)]
    #sub = imageLib.subimage(image,startRow,endRow,startCol,endCol)

    output = imageLib.meanThreshold(sub,thresholdFactor)

    M = cv2.moments(output)

    #convert the center of the points in the subimage back to frame coordinates
    #if no moment is found (zero division) OR if the momement center found is too far away
    # (maxDetectionDistance) then just use the estimated coordinate (input as the center)

    m00 = M["m00"]
    if ( m00 > 0 ):
        cX = int(M["m10"] / M["m00"]) + startCol
        cY = int(M["m01"] / M["m00"]) + startRow
        if (abs(cX - pX) > maxDetectionDistance or abs(cY - pY) > maxDetectionDistance):
            cX = pX
            cY = pY
    elif ( m00 == 0 ): # if no point is detected, use the original point
        cX = pX
        cY = pY

    center = (int(cX),int(cY))

    return center

def generateSpotPoint( startPoint, blockPoint, distance):
    (x0, y0) = startPoint # get the first (and only) start point
    #(px, py) = blockPoint
    #block points are 1 indexed in the gal file, subtract to get 0 index
    (px, py) = tuple(np.subtract(blockPoint, (1, 1)))
    res = ( x0+(distance*py),y0+(distance*px) )
    return res

def getMeanIntensityOfCircle(img, point, spotRadius: int):

    mask = np.zeros((img.shape[0],img.shape[1]), np.uint8)
    cv2.circle(mask,point,spotRadius,1,thickness=cv2.FILLED)
    return cv2.mean(img,mask)[0]

def getMedianIntensityOfBackground(img, point, backgroundRadius:int,backgroundThickness:int):

    #create a masked array to calculate the median easily
    #masked values (1 values) are ignored by the calculation
    #the region of interest is unmasked (0 values)
    backgroundMask = np.ones((img.shape[0],img.shape[1]),np.uint8)
    cv2.circle(backgroundMask,point,backgroundRadius,0,backgroundThickness)
    bg = backgroundMask.astype(bool)
    maskedBackground = np.ma.masked_array(img,bg)
    return np.ma.median(maskedBackground)

def annotatePoints(image, points, label, displayThresholdFactor: int, circleRadius:int,backgroundRadius:int,backgroundThickness:int):
    res = imageLib.imageToColorImage(image, 2)
    (width,height) = image.shape
    labelOffset = 16
    cv2.putText(res,label,(labelOffset,labelOffset),0,.50,(255,255,0),1,cv2.LINE_AA)
    for p in points:
        cv2.circle(res,p,circleRadius,(255,0,0),2)
        cv2.circle(res,p,backgroundRadius,(0,255,0),backgroundThickness)
    return res

#looking up each well's origin coords in the product definition dictionary
#subtracting the scan coords and dividing by the resolution
#to get the first feature coords in pixel space
def calculateFirstFeatureCoordsPixels(scanWells, productWells, scanResolution ):
    scanWellCoordsDict = { (scanWell['row']+scanWell['column']).upper():(scanWell['originX'],scanWell['originY'])  for scanWell in scanWells }
    productWellCoordsDict ={ (well['row']+well['column']).upper():(well['firstFeatureX'],well['firstFeatureY']) for well in productWells }
    def convertCoords(originXY, featureXY, resolution):
        offset = tuple(map(operator.sub, featureXY, originXY))
        result = tuple(ti/resolution for ti in offset)
        return result
    firstFeatureDict = {  well:convertCoords(coords,productWellCoordsDict.get(well),scanResolution)
                          for (well,coords) in scanWellCoordsDict.items() }
    return firstFeatureDict

def get96WellMap():
    resultRows = [ str(chr(x)) for x in [*range(ord('A'), ord('H') + 1)] ]
    resultCols = [*range(1,13)]
    return resultRows,resultCols