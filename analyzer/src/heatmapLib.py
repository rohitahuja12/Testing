import random
import cv2

import numpy as np
import math

import sys
import log
logger = log.getLogger('analyzer.src.heatmapLib')

#how to use findSpots function to find control spot in pArray
#res = il.findSpots(img,20,30,5000) <-params worked for Scott Milk data


def generateHeatMapTestData(maxValue):
    result = {}
    letters = "ABCDEFGH"
    rows, cols = 7, 12
    currentValue = maxValue
    for i in range(0,rows):
        for j in range(0,cols):
            if (i<100):
                rowString = letters[i]
                colString = str(j+1)
                address = rowString+colString
                result[address] = currentValue
                currentValue = currentValue - 8000
        currentValue = maxValue
    return result

def convertIndexToAddress(indexTuple):
    letters = "ABCDEFGH"
    r,c = indexTuple[0],indexTuple[1]
    address = None
    if ( r < 8 and c < 12):
        rowString = letters[r]
        colString = str(c+1)
        address = rowString+colString
    return address

def createHeatMap ( intensityDict, titleName, maxIntensity, blankIntensity, colorMap ):
    logger.info(f"Creating heatmap for {titleName}")
    logger.info(f"Min intensity: {blankIntensity} and Max intensity: {maxIntensity} ")
    width, height = 550,420
    wellX, wellY = 68, 100 #was 84
    rowLabelOriginX, rowLabelOriginY = 20, wellY+10 #was 94
    colLabelOriginX, colLabelOriginY = 58, wellY-30 #was 54
    deltaX, deltaY = 40,40
    circleSize = 18
    rows, cols = 8, 12
    font1 = cv2.FONT_HERSHEY_SIMPLEX
    font2 = cv2.FONT_HERSHEY_DUPLEX
    colFontScale = .75
    colThickness = 1
    digitAdjustment = 7
    titleX, titleY = 20, 32
    lineThickness = -1 #special code for cv2 circle that produces a filled circle
    darkGray = (10,10,10)
    backgroundColor = (245,245,245) #(222,200,200)
    letters = "ABCDEFGH"

    #filter 0's
    if blankIntensity == 0:
        blankIntensity = 1
        logger.info("Found a minimum intensity of 0 during heatmap generation.  Changing to 1 to display log scale.")
    for k,v in intensityDict.items():
        if v == 0:
            newEntry = {k:1}
            intensityDict.update(newEntry)
            logger.info("Found an intensity of 0 during heatmap generation.  Changing to 1 to display log scale.")

    logBlankIntensity = math.log(blankIntensity, 10)
    logMaxIntensity = math.log(maxIntensity, 10)-logBlankIntensity
    logIntensityDict = {k:math.log(v, 10)-logBlankIntensity for k,v in intensityDict.items()}

    img = np.zeros([height,width,3],dtype=np.uint8)
    cv2.rectangle(img, (0,0),(width-1,height-1),backgroundColor,-1)
    cv2.putText(img,titleName,(titleX,titleY),font2,.9,[0,0,0],1,cv2.LINE_AA)

    data = np.zeros([rows,cols],dtype=np.float32)
    emptyWells = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            ii = chr(ord("A")+i) # "ABCD..."
            jj = str(j+1) #"1234.."
            address = (ii,jj)
            if (address in logIntensityDict):
                data[i][j] = logIntensityDict[address]
            else:
                emptyWells.append((i,j))

    maxRow = np.ones([cols],dtype=np.float32)*logMaxIntensity #create a max intensity row to normalize with
    maxedData = np.append(data,[maxRow],axis=0) #add in the max value row for the plate
    norm = cv2.normalize(maxedData, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    colorized = cv2.cvtColor(norm[:-1], cv2.COLOR_GRAY2BGR) #remove the max value row for the plate
    mapped = cv2.applyColorMap(colorized,colorMap)

    #fill in circles
    for j in range(cols):
        x = wellX + (j*deltaX)
        colLabelX = colLabelOriginX + (j*deltaX)
        if j+1>9:
            colLabelX = colLabelX - digitAdjustment
        cv2.putText(img,str(j+1),(colLabelX,colLabelOriginY),font1,colFontScale,[0,0,0],colThickness,cv2.LINE_AA)

        for i in range(rows):
            y = wellY + (i*deltaY)
            colorValue =mapped[i][j]
            colorTuple = (int(colorValue[0]),int(colorValue[1]),int(colorValue[2]))

            #if the well address is in the empty list, fill it with the empty color.  Otherwise, fill it with the intensity color
            if (i,j) in emptyWells:
                cv2.circle(img, (x,y), circleSize,backgroundColor, lineThickness, lineType=cv2.LINE_AA)
                #logger.info(f'Empty well at address: {i},{j}')
            else:
                cv2.circle(img, (x,y), circleSize, colorTuple, lineThickness, lineType=cv2.LINE_AA)
                #logger.info(f'Filled well at address: {i},{j} with color {colorTuple}')

            #outline the well circle
            cv2.circle(img, (x,y), circleSize, darkGray, 1, lineType=cv2.LINE_AA)

            rowLabelY = rowLabelOriginY + (i*deltaY)
            if j == 0:
                cv2.putText(img,letters[i],(rowLabelOriginX,rowLabelY),font1,1,[0,0,0],colThickness,cv2.LINE_AA)
        y = wellY

    legend = generateLegendImage(colorMap, int(width/2) ,15)
    #cv2.imwrite("legend.png",legend)

    xOffset = int(width/2)-25
    yOffset = 30
    img[yOffset:yOffset+legend.shape[0], xOffset:xOffset+legend.shape[1]] = legend
    intensityString = "PLATE MAX INTENSITY: "+f'{maxIntensity:,}'
    cv2.putText(img,intensityString,(xOffset+20,titleY-10),font1,.5,[0,0,0],1,cv2.LINE_AA)
    #heatMapFileName = "heatmap_"+titleName+".png"
    #cv2.imwrite(heatMapFileName,img)
    (B,G,R) = cv2.split(img)
    img = cv2.merge((R,G,B))
    return img

def generateLegendImage(colorMap,width,height):
    row = np.linspace(0,256,width,dtype=np.float32)
    legend=np.tile(row, (height,1))
    norm = cv2.normalize(legend, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    colorized = cv2.cvtColor(norm, cv2.COLOR_GRAY2BGR)
    mapped = cv2.applyColorMap(colorized,colorMap)
    cv2.rectangle(mapped,(0,0),(width-1,height-1),(0,0,0),1)
    return mapped
