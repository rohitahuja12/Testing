import sys
sys.path.insert(0, '.')
import base64
import core.logging.log as log
import numpy as np
import os
import os.path
import threading
import time
import AsiCamera2Types as asi
import asi_camera_client as client
from core.codec.artifact_codec import ArtifactCodec
from core.asynchronous.class_lock_decorator import withClassLock

logger = log.getLogger("controller_camera.main")
codec = ArtifactCodec()

class CameraManager():

    intCameraID = -1
    name = None
    eightBit = False
    session = None
    sensorMicronsPerPixelX = None
    sensorMicronsPerPixelY = None
    hardBin = None
    softBin = 1
    sensorWidth = None
    sensorHeight = None
    roiW = None
    roiH = None
    roiX = None
    roiY = None
    isColorCamera = None
    gain = None
    mirrorX = None
    mirrorY = None
    rotation = None
    clientLock = None

    def __init__(self, imageQueue):
        self.imageQueue = imageQueue
        self.client = client

    @withClassLock
    def disconnect(self):
        pass

    @withClassLock
    def connect(self):
        logger.info('connecting camera...')
        
        # get SDK version from the library
        sdkversion = self.client.ASIGetSDKVersion()
        logger.info(f"SDK version = {sdkversion}")
        
        # get the number of connected cameras
        nCams = self.client.ASIGetNumOfConnectedCameras()
        logger.info(f"Total number of connected cameras = {nCams}")
        if nCams == 0 or nCams>1:
            raise Exception("Found {nCams} connected cameras, a single camera connection is required.")
        cameraIndex = 0

        # get camera info without connecting
        camInfo = self.client.ASIGetCameraProperty(cameraIndex)
        logger.info("ASI properties:")
        for i in camInfo:
            logger.info(f"{i} -> {camInfo[i]}" )
        self.name = camInfo['Name']
        self.intCameraID = camInfo['CameraID']
        self.sensorWidth = camInfo['MaxWidth']
        self.sensorHeight = camInfo['MaxHeight']
        self.sensorMicronsPerPixelX = camInfo['PixelSize']
        self.sensorMicronsPerPixelY = camInfo['PixelSize']
        self.isColorCamera = camInfo["IsColorCam"]
        
        # connect to the camera
        self.client.ASIOpenCamera(self.intCameraID)

        # initialize the camera
        self.client.ASIInitCamera(self.intCameraID)

    @withClassLock
    def preset(self):
        # initialize some camera settings
        if self.isColorCamera:
            # monobin
            self.client.ASISetControlValue(self.intCameraID, asi.AsiControlType.ASI_MONO_BIN, True, asi.AsiBool.ASI_FALSE)
            self.sensorMicronsPerPixelX = self.sensorMicronsPerPixelX*2
            self.sensorMicronsPerPixelY = self.sensorMicronsPerPixelY*2
            self.hardBin = 2
        else:
            self.hardBin = 1
        # set image format and bin
        if self.eightBit:
            imgType = asi.AsiImgType.ASI_IMG_RAW8
        else:
            imgType = asi.AsiImgType.ASI_IMG_RAW16
        self.roiW = self.sensorWidth // self.hardBin
        self.roiH = self.sensorHeight // self.hardBin
        self.roiX = 0
        self.roiY = 0
        self.client.ASISetROIFormat(self.intCameraID, self.roiW, self.roiH, self.hardBin, imgType)
        # set gain to HCG value for recognized cameras
        if self.name=='ZWO ASI662MC':
            self.gain = 252 
            self.client.ASISetControlValue(self.intCameraID, asi.AsiControlType.ASI_GAIN, self.gain, asi.AsiBool.ASI_FALSE)
        else:
            logger.info("WARNING: unable to preset gain")

    @withClassLock
    def setGain(self, gain: int):
        self.client.ASISetControlValue(self.intCameraID, asi.AsiControlType.ASI_GAIN, self.gain, asi.AsiBool.ASI_FALSE)

    @withClassLock
    def getGain(self, gain: int):
        ret = self.client.ASIGetControlValue(self.intCameraID, asi.AsiControlType.ASI_GAIN)
        return ret[0]
    
    @withClassLock
    def setRoi(self, x: int, y: int, w: int, h: int):
        if x<0 or y<0 or w<=0 or h<=0 or (x+w)>self.sensorWidth//self.hardBin or (y+h)>self.sensorHeight//self.hardBin:
            raise Exception(f"Unable to set ROI x={x},y={y},w={w},h={h} on camera sensor ({self.sensorWidth//self.hardBin}x{self.sensorHeight//self.hardBin})")
        self.roiW = w
        self.roiH = h
        self.roiX = x
        self.roiY = y

    @withClassLock
    def getRoi(self) -> [int,int,int,int]:
        return [self.roiX,self.roiY,self.roiW,self.roiH]

    @withClassLock
    def setBin(self, bin: int):
        #raise Exception(f"Software binning is not implemented yet")
        if bin<=0 or bin>self.sensorWidth or bin>self.sensorHeight:
            raise Exception(f"Unable to set bin={bin} on camera sensor ({self.roiW}x{self.roiH})")
        self.softBin = bin

    @withClassLock
    def getBin(self) -> int:
        return self.softBin

    @withClassLock
    def disconnect(self):
        self.client.ASICloseCamera(self.intCameraID)

    @withClassLock
    def getInfo(self) -> dict:
        d = self.client.ASIGetCameraProperty(self.cameraIndex)
        logger.info("ASI properties:")
        for i in d:
            logger.info(f"{i} -> {d[i]}" )
        return d

    @withClassLock
    def getSerialNumber(self) -> str:
        d = self.client.ASIGetSerialNumber(self.cameraID)
        logger.info("ASI properties:")
        for i in d:
            logger.info(f"{i} -> {d[i]}" )
        return d

    @withClassLock
    def expose(self, millis: int) -> str:
        '''
        And asyncronous expose method which returns an identifier immediately. The resulting image will appear on the image stream with the returned identifier as a prefix.
        '''
        imageId = os.urandom(4)
        threading.Thread(
            target=self._expose, 
            args=(millis, imageId)
        ).start()
        return imageId.hex()

    @withClassLock
    def exposeSync(self, millis: int) -> str:
        '''
        Returns a base64 encoded tiff image synchronously
        '''
        imageId = os.urandom(4)
        img = self._expose(millis, imageId)
        imgbytes = codec.arrayToTiff(img)
        return base64.b64encode(imgbytes).decode('ascii')

    @withClassLock
    def _expose(self, millis: int, imageId: str) -> np.ndarray:

        # set exposure
        self.client.ASISetControlValue(self.intCameraID, asi.AsiControlType.ASI_EXPOSURE, millis*1000, asi.AsiBool.ASI_FALSE)

        # Start exposure!
        logger.info(f'exp for {millis} ms')
        self.client.ASIStartExposure(self.intCameraID, asi.AsiBool.ASI_FALSE)

        # Start watching camera state
        expStatus = self.client.ASIGetExpStatus(self.intCameraID)
        #logger.info(f'expStatus = {expStatus}')
        while (expStatus == 1):#asi.AsiExposureStatus.ASI_EXP_WORKING):
            time.sleep(0.1)
            expStatus = self.client.ASIGetExpStatus(self.intCameraID)
            #logger.info(f'expStatus = {expStatus}')

        # Load image from camera
        #imageMetaData = self.client.ArtemisGetImageData(self.handle)
        img = self.client.ASIGetDataAfterExp(
            self.intCameraID,
            self.sensorWidth // self.hardBin,
            self.sensorHeight // self.hardBin, 
            self.eightBit).copy()

        # Extract ROI region
        img = img[self.roiY : self.roiY+self.roiH, :]
        img = img[:, self.roiX : self.roiX+self.roiW]

        # bin
        img = img.reshape(self.roiH//self.softBin, self.softBin, self.roiW//self.softBin, self.softBin).sum(3).sum(1)
        img = (img // (self.softBin*self.softBin)).astype(np.uint16)

        self.imageQueue.put((imageId, img))
        return img
