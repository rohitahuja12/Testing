import asyncio
import ArtemisTypes
import asyncio
import atik_infinity_client as client
import base64
import apiClient
import functools 
import json
import lib_hardware_interface.client as hwclient
import log
import numpy as np
import os
import sys
import threading
import time
import timing
from artifactCodec import ArtifactCodec
from contextlib import asynccontextmanager
from coords import CoordTriplet
from datetime import datetime
from multiprocessing import Process
from readerCacheHelper import getEncodedCachedValueOrRunFetch
from utils.apiAuthProvider import APIAuthProvider
logger = log.getLogger("controller_camera.cameraManager")
codec = ArtifactCodec()
api = apiClient.APIClient(APIAuthProvider())

def getReader(readerSerial):

    async def _fetch():
        readers = await api.getAll('readers', {'serialNumber':readerSerial})
        if not readers:
            raise Exception(f"Failed to retrieve reader configuration with serial {readerSerial}")
        reader = readers[0]
        return reader

    reader = asyncio.run(getEncodedCachedValueOrRunFetch(
        key = 'reader',
        fetch = _fetch))

    return reader

def getReaderSerial(boardTransport):

    async def _fetch():

        board = hwclient.HardwareClient(boardTransport)
        while True:
            try:
                readerSerial = board.getSerialNumber()
                break
            except Exception as e:
                logger.warn(f'Error connecting to board, retrying. {e}')
                time.sleep(1)
        return readerSerial

    readerSerial = asyncio.run(getEncodedCachedValueOrRunFetch(
        key = 'readerSerial',
        fetch = _fetch))

    return readerSerial

def withClassLock(f):
    @functools.wraps(f)
    def _inner(self, *args, **kwargs):
        threadId = threading.get_ident()
        while True:
            if self.clientLock == threadId:
                # lock acquired, begin communicatino
                break
            while self.clientLock != None:
                time.sleep(0)
            self.clientLock = threadId
        try:
            res = f(self, *args, **kwargs)
        finally:
            # release lock
            self.clientLock = None
        return res
    return _inner

# controls sessions,
# houses initialization data
# ensures new sessions have been 
# setup the same as the previous session
class CameraManager():

    handle = None
    eightBit = False
    session = None
    sensorMicronsPerPixelX = None
    sensorMicronsPerPixelY = None
    mirrorX = None
    mirrorY = None
    rotation = None
    clientLock = None

    def __init__(self, imageQueues, boardTransport):
        self.imageQueues = imageQueues
        self.client = client
        self.boardTransport = boardTransport

        # get settings from api (or cache in future)
        boardClient = hwclient.HardwareClient(self.boardTransport)
        readerSerial = boardClient.getSerialNumber()
        while True:
            try:
                logger.info(f'Retrieving reader configuration...')
                serial = getReaderSerial(boardTransport)
                readerConfig = getReader(serial)
                logger.info(f'Retrieved reader configuration {readerConfig}')
                time.sleep(5)
                break
            except Exception as e:
                logger.error(f'Failed to retrieve reader configuration, retrying in 5s: {e}')

        # write applicable settings into current camera state
        self.mirrorX = readerConfig['cameraMirrorImageX']
        self.mirrorY = readerConfig['cameraMirrorImageY']
        self.rotation = readerConfig['cameraRotateImageDeg']
        self.totalMagnification = readerConfig['totalMagnification']
        self.objectiveFovX = readerConfig['objectiveFovDimsX']
        self.objectiveFovY = readerConfig['objectiveFovDimsY']
        self.binX = readerConfig['cameraBinX']
        self.binY = readerConfig['cameraBinY']


    @withClassLock
    def connect(self):

        logger.info('connecting camera')
        self.handle = self.client.ArtemisConnect(0)
    
        if self.handle == None:
            raise Exception("Failed to connect. Try again.")
        if self.handle == 0:
            raise Exception("No camera found.")

        logger.info('connected camera successfully...')

    @withClassLock
    def disconnect(self):

        self.client.ArtemisDisconnect(self.handle)


    @withClassLock
    def setRotation(self, rotation: int) -> int:
        self.rotation = rotation
        return self.rotation
    def getRotation(self) -> int:
        return self.rotation

    @withClassLock
    def setTotalMagnification(self, totalMagnification: int) -> int:
        self.totalMagnification = totalMagnification
        return self.totalMagnification
    def getTotalMagnification(self) -> int:
        return self.totalMagnification

    @withClassLock
    def setObjectiveFovX(self, objectiveFovX: int) -> int:
        self.objectiveFovX = objectiveFovX
        return self.objectiveFovX
    def getObjectiveFovX(self) -> int:
        return self.objectiveFovX

    @withClassLock
    def setObjectiveFovY(self, objectiveFovY: int) -> int:
        self.objectiveFovY = objectiveFovY
        return self.objectiveFovY
    def getObjectiveFovY(self) -> int:
        return self.objectiveFovY

    @withClassLock
    def setMirrorX(self, mirrorX: bool) -> bool:
        self.mirrorX = mirrorX
        return self.mirrorX
    def getMirrorX(self) -> bool:
        return self.mirrorX

    @withClassLock
    def setMirrorY(self, mirrorY: bool) -> bool:
        self.mirrorY = mirrorY
        return self.mirrorY
    def getMirrorY(self) -> bool:
        return self.mirrorY

    @withClassLock
    def getInfo(self) -> dict:
        return self.client.ArtemisProperties(self.handle)

    @withClassLock
    def getName(self) -> str:
        return self.client.ArtemisDeviceName(self.handle)

    @withClassLock
    def getSerial(self) -> str:
        return self.client.ArtemisDeviceSerial(self.handle)

    @withClassLock
    def getBin(self) -> str:
        # return self.client.ArtemisGetBin(self.handle)
        return {'x': self.binX, 'y': self.binY}

    @withClassLock
    def setBin(self, x:int, y:int) -> int:
        # return self.client.ArtemisBin(self.handle, x, y)
        self.binX = x
        self.binY = y
        return {'x': self.binX, 'y': self.binY}

    @withClassLock
    def getSensorMicronsPerPixelX(self):
        if not self.sensorMicronsPerPixelX:
            info = self.getInfo()
            if not info: 
                return info
            self.sensorMicronsPerPixelX = info['PixelMicronsX']
            self.sensorMicronsPerPixelY = info['PixelMicronsY']
        return self.sensorMicronsPerPixelX * self.binX

    @withClassLock
    def getSensorMicronsPerPixelY(self):
        if not self.sensorMicronsPerPixelY:
            info = self.getInfo()
            if not info:
                return info
            self.sensorMicronsPerPixelX = info['PixelMicronsX']
            self.sensorMicronsPerPixelY = info['PixelMicronsY']
        return self.sensorMicronsPerPixelY * self.binY

    @withClassLock
    def expose(self, millis: int) -> str:

        imageId = os.urandom(4)
        threading.Thread(
            target=self._expose, 
            args=(millis, imageId)
        ).start()
        return imageId.hex()

    # if this mthod is called from the main thread, it will block other requests 
    # from being processed until exposeSync returns. This only really affects 
    # functions without the 'withClassLock' decorator, which cannot be processed while
    # the sync or async expose is runing.
    @withClassLock
    def exposeSync(self, millis: int) -> str:
        
        imageId = os.urandom(4)
        img = self._expose(millis, imageId)
        imgbytes = codec.arrayToTiff(img)
        return base64.b64encode(imgbytes).decode('ascii')


    @withClassLock
    def _expose(self, millis: int, imageId: str) -> np.ndarray:

        self.connect()

        # Apply settings to current camera instance
        self.client.ArtemisBin(self.handle, self.binX, self.binY)

        # Start exposure!
        logger.info(f'exp for {millis}ms')
        self.client.ArtemisStartExposureMS(self.handle, millis)

        # Start watching camera state
        cameraState = ArtemisTypes.ArtemisCameraState.CAMERA_IDLE
        while (not self.client.ArtemisImageReady(self.handle)):
            newState = self.client.ArtemisCameraState(self.handle)
            if (newState != cameraState):
                cameraState = newState

            time.sleep(0)

        # Load image from camera
        imageMetaData = self.client.ArtemisGetImageData(self.handle)
        img = self.client.ArtemisImageBuffer(
            self.handle,
            imageMetaData["width"], 
            imageMetaData["height"],
            self.eightBit).copy()

        # Extract ROI region
        if self.objectiveFovX:
            roih = self.totalMagnification*self.objectiveFovX
            roiHPixels = roih // self.getSensorMicronsPerPixelY()
            cropHPixels = int((imageMetaData["height"] - roiHPixels) // 2)
            img = img[cropHPixels:-cropHPixels,:]
        if self.objectiveFovY:
            roiw = self.totalMagnification*self.objectiveFovY
            roiWPixels = roiw // self.getSensorMicronsPerPixelX()
            cropWPixels = int((imageMetaData["width"] - roiWPixels) // 2)
            img = img[:, cropWPixels:-cropWPixels]

        # Apply transforms
        if self.mirrorX:
            img = np.fliplr(img)

        if self.mirrorY:
            img = np.flipud(img)

        if self.rotation:
            turns = self.rotation//90
            img = np.rot90(img, k=turns, axes=(1,0))
    
        for q in self.imageQueues:
            q.put((imageId, img))

        return img 
