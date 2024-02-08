import random
import cv2

import numpy as np

import sys
sys.path.insert(0,"./analyzer/src")
import curveFitter
sys.path.remove("./analyzer/src")


def generateSpotPoint( startPoint, blockPoint, distance):
    (x0, y0) = startPoint # get the first (and only) start point
    (px, py) = blockPoint
    res = ( x0+(distance*py),y0+(distance*px) )
    return res

def createArrayTestImage( width:int, height:int):

    print("Creating test image!")

    blockPoints = [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                   (1,1),(1,2),(1,3),(1,4),(1,5),(1,6)]

    a = 60
    b = 1
    c = 70
    d = 90000

    backgroundIntensity = a - 20

    initialConcentration = 1000
    dilutionFactor = 5
    numberOfStandards = 7

    concentrations = []
    for r in range(0,numberOfStandards):
        concentrations.append( initialConcentration / (dilutionFactor**r) )
    concentrations.append(1e-20)
    standardIntensities = [ curveFitter.logistic4( conc, a,b,c,d ) for conc in concentrations ]

    #print ("Test value: ",curveFitter.logistic4( 1000, a,b,c,d ) )

    print(*concentrations)
    print(*standardIntensities)

    startPoint = (55,40)
    spacing = 40
    diameter = 20

    imagesCol1 = []
    imagesCol2 = []
    imagesCol3 = []
    index=1
    for stdIntensity in standardIntensities:
        data = backgroundIntensity * np.ones( (height, width), dtype=np.float32)
        for p in blockPoints:
            aPoint = generateSpotPoint(startPoint,p,spacing)
            random.seed(p)
            randIntensity = stdIntensity * random.uniform(0.8, 1.1)
            #cv2.circle(data,aPoint,int(diameter/2),stdIntensity,-1)
            cv2.circle(data,aPoint,int(diameter/2),randIntensity,-1)
        index = index+1
        imagesCol1.append(data)
        imagesCol2.append(data)
        if index == 3 or index == 4:
            imagesCol3.append(data)

    return imagesCol1+imagesCol2+imagesCol3


