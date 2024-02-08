import sys
sys.path.insert(0, './common')
import asyncio
import base64
import apiClient
import io
import json
import log
import productHelper
import artifactCodec
from utils.apiAuthProvider import APIAuthProvider
from readerCacheHelper import getCache, getCalibrationValue
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from math import sin, cos, radians
from zipfile import ZipFile


api = apiClient.APIClient(APIAuthProvider())
codec = artifactCodec.ArtifactCodec()
logger = log.getLogger("svc_locations.locationManager")

@dataclass
class Point:
    x: float
    y: float

@dataclass_json
@dataclass
class ReaderPoint():
    name: str
    type: str
    movesWithStage: bool
    x: float
    y: float
    x_px: float
    y_px: float

"""
overlay one coordinate plane onto another
"""
# rotate a point by an angle
# direction is from positive x axis
# toward positive y axis
def rotate(point, theta):
    (x,y) = point
    theta = radians(theta)
    return round(x*cos(theta)-y*sin(theta)), \
           round(x*sin(theta)+y*cos(theta))

def translate(point, translation):
    (x,y) = point
    (xTrans, yTrans) = translation
    return (x+xTrans, y+yTrans)

def invertAxes(point, invert):
    (x,y) = point
    (xInvert, yInvert) = invert
    return (-x if xInvert else x), \
           (-y if yInvert else y)

def scale(point, scaleFactor):
    (x,y) = point
    (xScale, yScale) = scaleFactor
    return (x*xScale, y*yScale)

def convertCoordinateSystems(
    point,   # point in initial coordinates
    rotation,# Degrees of rotation to be applied.
            # Direction is from positive x axis 
            # toward positive y axis.
    offset, # translation to be applied
    invert,
    scaleFactors=(1,1)):# (bool,bool) invert axes

    point = invertAxes(point,invert)
    point = rotate(point,rotation)
    point = translate(point,offset)
    point = scale(point,scaleFactors)

    return point


def kitToStage(
    kitPoint,
    kitToAdapterRotation,
    kitToAdapterOffset,
    kitToAdapterInvert,
    adapterToStageRotation,
    adapterToStageOffset,
    adapterToStageInvert):

    def kitToAdapter(point):
        return convertCoordinateSystems(
            point = point,
            rotation = kitToAdapterRotation, 
            offset = kitToAdapterOffset, 
            invert = kitToAdapterInvert)

    def adapterToStage(point):
        return convertCoordinateSystems(
            point,
            rotation = adapterToStageRotation, 
            offset = adapterToStageOffset,
            invert = adapterToStageInvert)

    adapterPoint = kitToAdapter(kitPoint)
    stagePoint = adapterToStage(adapterPoint)

    return stagePoint

def stageToImage(
    stagePoint,
    stageToImageRotation,
    stageToImageOffset,
    stageToImageInvert,
    stageToImageScale
    ):

    return convertCoordinateSystems(
        point = stagePoint,
        rotation = stageToImageRotation,
        offset = stageToImageOffset,
        invert = stageToImageInvert,
        scaleFactors = stageToImageScale)

class LocationManager:

    def __init__(self, reader):
        logger.info(f'reader is {reader}')
        self.reader = reader
        self.nonProductPoints = [
            ReaderPoint(
                name="cameraCenter",
                type="reader",
                movesWithStage=False,
                x=0, y=0,
                x_px=0, y_px=0)
        ]

    def _xformKitToStage(self, x:int, y:int) -> tuple:
        return kitToStage(
            kitPoint = (x,y),
            kitToAdapterRotation = self.reader['kitToAdapterRotation'],
            kitToAdapterOffset = (
                self.reader['kitToAdapterOffsetX'],
                self.reader['kitToAdapterOffsetY']),
            kitToAdapterInvert = (
                self.reader['kitToAdapterInvertX'],
                self.reader['kitToAdapterInvertY']),
            adapterToStageRotation = self.reader['adapterToStageRotation'],
            adapterToStageOffset = (
                self.reader['adapterToStageOffsetX'],
                self.reader['adapterToStageOffsetY']),
            adapterToStageInvert = (
                self.reader['adapterToStageInvertX'],
                self.reader['adapterToStageInvertY'])
        )

    def _xformStageToImage(self, x:int, y:int) -> tuple:
        return stageToImage(
            stagePoint = (x,y),
            stageToImageRotation = self.reader['stageToImageRotation'],
            stageToImageOffset = (
                self.reader['stageToImageOffsetX'],
                self.reader['stageToImageOffsetY']),
            stageToImageInvert = (
                self.reader['stageToImageInvertX'],
                self.reader['stageToImageInvertY']),
            # scale here set with binning from reader.json doc
            # it will not update if the binning is manually changed.
            stageToImageScale = (
                self.reader['totalMagnification'] / \
                    self.reader['sensorMicronsPerPixelX'] / \
                    self.reader['cameraBinX'],

                self.reader['totalMagnification'] / \
                    self.reader['sensorMicronsPerPixelY'] / \
                    self.reader['cameraBinY'],
            )
        )

    def setProduct(self, productId:str) -> str:
        try:
            self.productId = productId
            self.product = asyncio.run(api.get('products', productId))
            
            self.productFeatures = productHelper.parseKitFeatures(json.dumps(self.product))
        except Exception as e:
            logger.error(e)
            raise

        return self.productId

    # returns top level only
    def getTopLevelPoints(self) -> list:
        return [
            *self.getChildPoints([]),
            *[p.to_dict() for p in self.nonProductPoints]
        ]

    def getPoint(self, path:list) -> dict:
        # if the point is a non-product point, resolve it and return
        npp = next((p for p in self.nonProductPoints if p.name == path), None)
        if npp:
            return npp.to_dict()

        # assume its a product point and look it up
        f,x,y = productHelper.getFeatureFromPath(self.productFeatures, path)
        x,y = self._xformKitToStage(x,y)
        if self.reader['applyCalibratedOffsetsXY']:
            x = x + getCalibrationValue('xoffset')
            y = y + getCalibrationValue('yoffset')
        x_px, y_px = self._xformStageToImage(x,y)
        return f and ReaderPoint(
            name=path,
            type="product",
            movesWithStage=True,
            x=x,
            y=y,
            x_px = int(x_px),
            y_px = int(y_px)
        ).to_dict()

    def getChildPoints(self, path:list) -> list:
        f,_,_ = productHelper.getFeatureFromPath(self.productFeatures, path)
        if self.reader['applyCalibratedOffsetsXY']:
            xoffset = getCalibrationValue('xoffset')
            yoffset = getCalibrationValue('yoffset')
        else:
            xoffset = 0
            yoffset = 0

        children = [
            [
                path+[name],
                # expands to feature, x, y
                *productHelper.getFeatureFromPath(
                    self.productFeatures, 
                    path+[name]) 
            ]
            for name, feat in f.features.items()
        ]
        # inefficient, i know
        res = []
        for fullpath, feat, x, y in children:
            stagept_x, stagept_y = self._xformKitToStage(x,y)
            stagept_x = stagept_x + xoffset
            stagept_y = stagept_y + yoffset
            imgpt = self._xformStageToImage(stagept_x, stagept_y)
            res.append(ReaderPoint(
                name=fullpath,
                type="product",
                movesWithStage=True,
                x=stagept_x,
                y=stagept_y,
                x_px=int(imgpt[0]),
                y_px=int(imgpt[1])
            ))
        res = [r.to_dict() for r in res]
        return res or None

    def _setAdapterToStageOffset(self, x: int, y: int) -> dict:
        self.reader['adapterToStageOffsetX'] = x
        self.reader['adapterToStageOffsetY'] = y
        return {'x': x, 'y': y}

    def _getAdapterToStageOffset(self) -> dict:
        return {
            'x': self.reader['adapterToStageOffsetX'], 
            'y': self.reader['adapterToStageOffsetY']
        }

    def setCorrectCalibratedXY(self, correct:bool) -> bool:
        self.reader['applyCalibratedOffsetsXY'] = correct
        return correct

    def getCorrectCalibratedXY(self) -> bool:
        return self.reader['applyCalibratedOffsetsXY']

