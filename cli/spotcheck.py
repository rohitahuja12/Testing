import sys
sys.path.insert(0,'./common')
sys.path.insert(0,'.')
import imageLib
import numpy as np
import artifactCodec
codec = artifactCodec.ArtifactCodec()
import cv2
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os

async def handle(args):

    current_time = datetime.now()
    time_part = current_time.strftime('%m-%d-%Y_%H-%M-%S')

    print(f"Started spot check at {time_part}.  Processing...")
    paramFile = args['<qcParams>']
    if paramFile == None:
        paramFile = os.path.join("cli","spotcheck","spotcheck-params.json")

    outputPath = args['<outputPath>']
    if outputPath == None:
        outputPath = ""

    with open (paramFile,'r') as file:
        paramDict = json.load(file)

    plateID = args["<plateID>"]

    output_dir = f"qc_{plateID}_{time_part}"

    inputFilePath = args["<imageFilePath>"]
    img = codec.readTiff(args["<imageFilePath>"])

    minNeighborhoodSize = paramDict["minimumSpotSize"]
    maxNeighborhoodSize = paramDict["maximumSpotSize"]
    thresholdValue =  paramDict["spotIntensityThresholdMultiplier"]
    maxDeviation =  paramDict["maxSpotLinearDeviation"]

    gridX = paramDict["gridOriginX"]
    gridY = paramDict["gridOriginY"]
    gridWindowWidth = paramDict["gridWindowWidth"]
    gridDeltaX = paramDict["gridDeltaX"]
    gridDeltaY = paramDict["gridDeltaY"]
    gridOrigin = (gridX,gridY)

    #from Product or GAL file eventually
    numberOfCols = 12
    rows = 'ABCDEFGH'
    cols = [i for i in range(1,numberOfCols+1)]
    spotDistance = 21
    spotArray = [ [0,1,1,1,1,1,0],
                  [1,1,1,1,1,1,1],
                  [1,1,0,0,0,1,1],
                  [1,1,0,1,0,1,1],
                  [1,1,0,0,0,1,1],
                  [1,1,1,1,1,1,1],
                  [0,1,1,1,1,1,0] ]
    #posPos is positive control position :)
    posPosRow = 3
    posPosCol = 3
    posPos = (posPosRow,posPosCol)

    #global stats
    avgRowSdev = 0
    avgColSdev = 0
    rowSdevSum = 0
    colSdevSum = 0
    rowSdevCount = 0
    colSdevCount = 0

    messageList = []

    feature = codec.readTiff(os.path.join("cli","spotcheck","spotcheck-feature.tif"))

    img2 = np.array(img)
    feature2 = np.array(feature)

    #remove nans from each image
    nan_mask_img = np.isnan(img2)
    nanCount = len(nan_mask_img)
    img2[nan_mask_img] = 0
    nan_mask_feature = np.isnan(feature2)
    feature2[nan_mask_feature] = 0

    displayImg = imageLib.imageToColorImage(img2)
    rawImg = imageLib.imageToColorImage(img2)

    sigma = "\u03C3"
    ############################
    #Create grid
    wells = []
    x = gridOrigin[0]
    y = gridOrigin[1]
    for r in rows:
        for c in cols:
            well = {}
            label = f'{r}{str(c)}'
            well['label']=label
            well['upperLeft']=(x,y)
            well['lowerRight']=(x+gridWindowWidth,y+gridWindowWidth)
            x = x + gridDeltaX
            wells.append(well)
        x = gridOrigin[0]
        y = y + gridDeltaY

    for well in wells:
        arrayRadius = 80
        w = 2 * arrayRadius

        pStart = well['upperLeft']
        pStop = well['lowerRight']

        cv2.rectangle(displayImg,pStart,pStop, (0,255,0), 2 )
        cv2.putText(displayImg,well['label'], (well['upperLeft'][0],well['upperLeft'][1]-4), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,255),2,cv2.LINE_AA)

        sub = img2[well['upperLeft'][1]:well['lowerRight'][1],well['upperLeft'][0]:well['lowerRight'][0]]
        res = cv2.filter2D(sub,-1,feature2)

        maxSub = np.max(sub)
        maxKer = np.max(feature2)
        maxVal = np.max(res)
        maxIndex = np.where(res==maxVal)

        maxResult = list(zip(maxIndex[1],maxIndex[0]))[0]
        rx = maxResult[0]
        ry = maxResult[1]
        #new control spot is found...
        nx = well['upperLeft'][0] + rx
        ny = well['upperLeft'][1] + ry
        cv2.circle(displayImg,(nx,ny),6,(255,0,0),1)
        well['foundCenter'] = (nx,ny)


    for well in wells:
        #if well['label'] == 'A1':
        if True:
            x = well['foundCenter'][0]
            y = well['foundCenter'][1]
            spotDistanceRadius = int(spotDistance/2)
            relativeCoordDict = {}
            for r, row in enumerate(spotArray):
                for c, value in enumerate(row):
                    if value == 1:
                        xDist = posPosRow - r
                        yDist = posPosRow - c
                        xDelta = xDist*spotDistance
                        yDelta = yDist*spotDistance
                        spotX = x - xDelta
                        spotY = y - yDelta
                        cv2.rectangle(displayImg,
                                      (spotX-spotDistanceRadius,spotY-spotDistanceRadius),
                                      (spotX+spotDistanceRadius,spotY+spotDistanceRadius),
                                      (0,255,255),
                                      1 )
                        spotSub = img2[spotY-spotDistanceRadius:spotY+spotDistanceRadius,spotX-spotDistanceRadius:spotX+spotDistanceRadius]
                        subMean = np.mean(spotSub) * thresholdValue
                        finalSpots = imageLib.findSpots(spotSub,minNeighborhoodSize,maxNeighborhoodSize,subMean)
                        numSpots = len(finalSpots)
                        if numSpots == 0:
                            well["isOutlier"]=True
                            messageList.append( {well['label']:f"position ({r+1},{c+1}) has {numSpots} spots"} )
                        elif numSpots > 1 :
                            well["isOutlier"]=True
                            messageList.append( {well['label']:f"position ({r+1},{c+1}) has {numSpots} spots"} )
                            #find the closest spot
                            subWidth, subLength = np.shape(spotSub)
                            expectedX = subWidth/2
                            expectedY = subLength/2
                            points_list = [(d['x'],d['y']) for d in finalSpots ]
                            nearestPoint = imageLib.findNearestPoint(points_list, (expectedX,expectedY))
                            finalX = spotX-spotDistanceRadius+nearestPoint[0]
                            finalY = spotY-spotDistanceRadius+nearestPoint[1]
                            cv2.circle(displayImg,(finalX,finalY),2,(255,0,255),-1)
                            #save the spot to the coord dict
                            coord = (r,c)
                            relX = finalX-x
                            relY = finalY-y
                            relativeCoordDict[coord] = (relX,relY)

                            #display the possible spots
                            for f in finalSpots:
                                finalX = spotX-spotDistanceRadius+f['x']
                                finalY = spotY-spotDistanceRadius+f['y']
                                cv2.circle(displayImg,(finalX,finalY),2,(255,255),-1)
                        else:
                           f = finalSpots[0]
                           finalX = spotX-spotDistanceRadius+f['x']
                           finalY = spotY-spotDistanceRadius+f['y']
                           cv2.circle(displayImg,(finalX,finalY),2,(255,0,255),-1)
                           #save the spot to the coord dict
                           coord = (r,c)
                           relX = finalX-x
                           relY = finalY-y
                           relativeCoordDict[coord] = (relX,relY)

            #adjust relative coords so that pos coord is (0,0)
            posCoords = relativeCoordDict[posPos]
            adjustedRelativeCoordDict = {}
            for index, coord in relativeCoordDict.items():
                ax = coord[0] - posCoords[0]
                ay = coord[1] - posCoords[1]
                adjustedRelativeCoordDict[index] = (ax,ay)
            well["detectedRelativeSpotCoordinates"] = adjustedRelativeCoordDict
            well["detectedRelativeSpotCenter"] = (well['foundCenter'][0]+posCoords[0],well['foundCenter'][1]+posCoords[1])

    #sanity check
    for well in wells:
        label = well['label']
        center = well['foundCenter']
        cx = center[0]
        cy = center[1]
        coords = well['detectedRelativeSpotCoordinates']
        #adjust center for testing purposes
        cx = well['detectedRelativeSpotCenter'][0]
        cy = well['detectedRelativeSpotCenter'][1]
        for index,point in coords.items():
           sx = cx + point[0] #- posPoint[0]
           sy = cy + point[1] #- posPoint[1]
           cv2.circle(displayImg,(sx,sy),4,(0,255,0),1)

    def fmtPt(point):
        p = "{:.2f}".format(point)
        return p

    #actual metrics calculation
    for well in wells:
        def group_by(items,dim):
            grouped = {}
            for item in items:
                if dim == "row":
                    value = item[0][1]
                else:
                    value = item[0][0]
                if value not in grouped:
                    grouped[value] = []
                grouped[value].append(item)
            return list(grouped.values())

        def calculate_linearity_stats(linePoints,dim):
            stats = {}
            #compute the sdev and mean of each row or column
            if dim == "row":
                targetIndex = 1
            else:
                targetIndex = 0
            for linePoint in linePoints:
                values = []
                for p in linePoint:
                    point = p[0]
                    coord = p[1]
                    values.append(coord[targetIndex])
                sdev = np.std(values,ddof=1)
                stats[point[targetIndex]] = { "mean":np.mean(values),"sdev":sdev}

            return stats

        pointsDict = well['detectedRelativeSpotCoordinates']
        pointList = list(pointsDict.items())
        rowPoints = group_by(pointList,"row")
        rowStats = calculate_linearity_stats(rowPoints,"row")
        well['rowStats'] = rowStats
        colPoints = group_by(pointList,"col")
        colStats = calculate_linearity_stats(colPoints,"col")
        well['colStats'] = colStats
        if 'isOutlier' not in well:
            well['isOutlier'] = False
        for r,v in rowStats.items():
            rowSdevSum = rowSdevSum + v['sdev']
            rowSdevCount = rowSdevCount +1
            if v['sdev'] > maxDeviation:
                well['isOutlier']=True
                messageList.append({well['label']: f"row {r} has a {sigma} of {fmtPt(v['sdev'])}"})
        for c,v in colStats.items():
            colSdevSum = colSdevSum + v['sdev']
            colSdevCount = colSdevCount + 1
            if v['sdev'] > maxDeviation:
                well['isOutlier']=True
                messageList.append({well['label']: f"col {c} has a {sigma} of {fmtPt(v['sdev'])}"})

    #count outliers for display purposes
    numOutliers = max( sum(1 for d in wells if d.get("isOutlier") == True), 2)
    scaleFactor = 1

    fig,axs = plt.subplots(nrows=numOutliers,ncols=2,figsize=(12,numOutliers*7))
    outlierRow = 0

    #general stats
    avgRowSdev = rowSdevSum / rowSdevCount
    avgColSdev = colSdevSum / colSdevCount

    #generate report
    for well in wells:
        if well['isOutlier'] == True:
            wellHeight = int( ( well['lowerRight'][1] - well['upperLeft'][1] ) / 2 )
            wellWidth = int ( ( well['lowerRight'][0] - well['upperLeft'][0] ) /2 )
            wellCenter = well['detectedRelativeSpotCenter']
            subRowsStart =  wellCenter[1] - wellHeight
            subRowsStop = wellCenter [1] + wellHeight
            subColsStart = wellCenter[0] - wellWidth
            subColsStop = wellCenter [0] + wellWidth
            imgSub = displayImg[subRowsStart:subRowsStop,subColsStart:subColsStop]
            (w,h,z) = np.shape(imgSub)
            imgSubScaled = cv2.resize(imgSub,(scaleFactor*w,scaleFactor*h),interpolation=cv2.INTER_LINEAR)

            axs[outlierRow, 0].imshow(imgSubScaled)
            axs[outlierRow, 0].set_title(well['label'],fontsize=32)
            axs[outlierRow,0].axis('off')

            pointsDict = well['detectedRelativeSpotCoordinates']
            pointList = list(pointsDict.items())
            rowPoints = group_by(pointList,"row")
            rowStats = well['rowStats']
            colPoints = group_by(pointList,"col")
            colStats = well['colStats']

            maxXValue = 0
            maxYValue = 0
            #find max x values for plotting
            for r in rowPoints:
                n = r[0][0][1]
                plotPoints = [ p2 for p1, p2 in r ]
                x,y = zip(*plotPoints)
                if max(x) > maxXValue:
                    maxXValue = max(x)
            for r in rowPoints:
                n = r[0][0][0]
                plotPoints = [ p2 for p1, p2 in r ]
                x,y = zip(*plotPoints)
                if max(y) > maxYValue:
                    maxYValue = max(y)

            #plot the points
            for r in rowPoints:
                n = r[0][0][1]
                rowMean = rowStats[n]["mean"]
                sdev = rowStats[n]["sdev"]
                plotPoints = [ p2 for p1, p2 in r ]
                x,y = zip(*plotPoints)
                rightX = maxXValue+10
                y_mean = rowMean
                axs[outlierRow,1].scatter(x,y,label="spots", color='red', s=100 )
                axs[outlierRow,1].plot(x,[y_mean]*len(x),color="lightgray",label=f"row {n} mean",linestyle="--")
                axs[outlierRow,1].text(rightX,y_mean,f"{sigma}y={fmtPt(sdev)}",fontsize=18)
                axs[outlierRow,1].invert_yaxis()
                axs[outlierRow,1].axis('off')

            for c in colPoints:
                bottomY = maxYValue+36
                n = c[0][0][0]
                colMean = colStats[n]["mean"]
                sdev = colStats[n]["sdev"]
                plotPoints = [ p2 for p1, p2 in c ]
                x,y = zip(*plotPoints)
                x_mean = colMean
                axs[outlierRow,1].plot([x_mean]*len(y),y,color="gray",label=f"col {n} mean",linestyle="--")
                axs[outlierRow,1].text(x_mean,bottomY,f"{sigma}x={fmtPt(sdev)}",fontsize=18,rotation=90)

            outlierRow = outlierRow+1


    plt.suptitle(f"QC Exception Report for {plateID} ({sigma}>={maxDeviation})",fontsize=20)
    plt.tight_layout(pad=5.0)

    finalOutputPath = os.path.join(outputPath,output_dir)
    if not os.path.exists(finalOutputPath):
        os.makedirs(finalOutputPath)
    plt.savefig(os.path.join(finalOutputPath,'qc.png'))
    compression_params = [cv2.IMWRITE_JPEG_QUALITY,70]
    cv2.imwrite(os.path.join(finalOutputPath,"plate_detected.jpg"),displayImg,compression_params)
    cv2.imwrite(os.path.join(finalOutputPath,"plate_raw.jpg"),rawImg, compression_params)

    current_datetime = datetime.now()
    datetime_string = current_datetime.strftime('%m-%d-%Y %I:%M %p')
    with open(os.path.join(finalOutputPath,"qc_report.txt"),"w",encoding="utf-8") as file:
        file.write(f"\nANOMALY REPORT for {finalOutputPath}\n\n")
        file.write(f"{datetime_string}\n\n")
        file.write(f"Input file: {inputFilePath}\n")
        file.write(f"Input params from {paramFile}:\n")
        file.write(f"{paramDict}\n\n")
        file.write(f"Found {nanCount} NaN pixels in input image file.\n\n")
        file.write(f"Average {sigma} of all rows: {avgRowSdev}\n")
        file.write(f"Average {sigma} of all cols: {avgColSdev}\n\n")
        if len(messageList) == 0:
            file.write("NO ANOMALIES FOUND.")
        for e in messageList:
            for k,v in e.items():
                file.write(f"{k}:{v}\n")

    current_time = datetime.now()
    time_part = current_time.strftime('%m-%d-%Y_%H-%M-%S')
    print(f"Finished spot check at {time_part}. Results directory: {finalOutputPath}")
