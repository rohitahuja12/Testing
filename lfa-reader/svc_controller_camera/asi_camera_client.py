# This file loads the .so file
# Hides all ctypes details from calling code
import AsiCamera2Types as asi
import typing
import os
import os.path
import subprocess
import asyncio
import ctypes as ct
import numpy as np
import core.logging.log as log
logger = log.getLogger('controller_camera.asi_camera_client')
import pyudev


phxHome = os.environ["PHOENIX_HOME"]

#libPath = os.path.join(phxHome, 'lfa-reader/svc_controller_camera/libASICamera2.so')
#logger.info(f"Libpath {libPath}, exists? {os.path.exists(libPath)}")

#_lib = ct.CDLL(libPath)
_lib = ct.CDLL('libASICamera2.so.1.33')

'''
---------- dll ----------
'''

# ASICAMERA_API char* ASIGetSDKVersion();
def ASIGetSDKVersion() -> str:
    _lib.ASIGetSDKVersion.restype = ct.POINTER(ct.c_char)
    buf = _lib.ASIGetSDKVersion()
    return ct.cast(buf, ct.c_char_p).value

'''
---------- Device ----------
'''

# ASICAMERA_API  int ASIGetNumOfConnectedCameras(); 
def ASIGetNumOfConnectedCameras():
    return _lib.ASIGetNumOfConnectedCameras()

# ASICAMERA_API  ASI_ERROR_CODE ASIOpenCamera(int iCameraID);
def ASIOpenCamera(iCameraID: int):
    _lib.ASIOpenCamera.restype = asi.AsiErrorCode
    res = _lib.ASIOpenCamera(iCameraID)
    if res != asi.AsiErrorCode.ASI_SUCCESS:
        raise Exception(f"Error opening camera {iCameraID}: "+str(res))

#ASICAMERA_API  ASI_ERROR_CODE ASIInitCamera(int iCameraID);
def ASIInitCamera(iCameraID: int):
    _lib.ASIInitCamera.restype = asi.AsiErrorCode
    res = _lib.ASIInitCamera(iCameraID)
    if res != asi.AsiErrorCode.ASI_SUCCESS:
        raise Exception(f"Error initializing camera {iCameraID}: "+str(res))

#ASICAMERA_API  ASI_ERROR_CODE ASICloseCamera(int iCameraID);
def ASICloseCamera(iCameraID: int):
    _lib.ASICloseCamera.restype = asi.AsiErrorCode
    res = _lib.ASICloseCamera(iCameraID)
    if res != asi.AsiErrorCode.ASI_SUCCESS:
        raise Exception(f"Error closing camera {iCameraID}: "+str(res))

#ASICAMERA_API ASI_ERROR_CODE ASISetControlValue(int  iCameraID, ASI_CONTROL_TYPE  ControlType, long lValue, ASI_BOOL bAuto);
def ASISetControlValue(iCameraID: int, control: asi.AsiControlType, value: int, auto: asi.AsiBool):
    _lib.ASISetControlValue.restype = asi.AsiErrorCode
    res = _lib.ASISetControlValue(iCameraID, control.value, value, auto.value)
    if res != asi.AsiErrorCode.ASI_SUCCESS:
        raise Exception(f"Error setting control {str(control)} to {value} auto={str(auto)} for camera {iCameraID}: "+str(res))

#ASICAMERA_API ASI_ERROR_CODE ASIGetControlValue(int  iCameraID, ASI_CONTROL_TYPE  ControlType, long *plValue, ASI_BOOL *pbAuto);
def ASIGetControlValue(iCameraID: int, control: asi.AsiControlType):
    _lib.ASIGetControlValue.restype = asi.AsiErrorCode
    value = ct.c_long()
    auto = ct.c_bool()
    res = _lib.ASISetControlValue(iCameraID, control.value, ct.byref(value), ct.byref(auto))
    if res == asi.AsiErrorCode.ASI_SUCCESS:
        # return control value and auto setting
        response = [value,auto]
        return response
    raise Exception(f"Error getting control value "+str(control)+" for camera {iCameraID}: "+str(res))

#ASICAMERA_API  ASI_ERROR_CODE ASISetROIFormat(int iCameraID, int iWidth, int iHeight,  int iBin, ASI_IMG_TYPE Img_type); 
def ASISetROIFormat(iCameraID: int, width: int, height: int, bin: int, imgType: asi.AsiImgType):
    _lib.ASISetROIFormat.restype = asi.AsiErrorCode
    res = _lib.ASISetROIFormat(iCameraID, width, height, bin, imgType.value)
    if res != asi.AsiErrorCode.ASI_SUCCESS:
        raise Exception(f"Error setting image format (w={width},h={height},bin={bin},imgType={str(imgType)}) for camera {iCameraID}: "+str(res))

'''
---------- Camera Info ----------
'''
# ASICAMERA_API ASI_ERROR_CODE ASIGetCameraProperty(ASI_CAMERA_INFO *pASICameraInfo, int iCameraIndex);
def ASIGetCameraProperty(iCameraIndex: int) :
    properties = asi.AsiCameraInfo()
    _lib.ASIGetCameraProperty.restype = asi.AsiErrorCode
    res = _lib.ASIGetCameraProperty(ct.byref(properties),iCameraIndex)
    def toString(x):
        return x.decode('ascii') if isinstance(x, typing.ByteString) else x
    if res == asi.AsiErrorCode.ASI_SUCCESS:
        # return properties
        response = { 
            k: toString(getattr(properties, k))
            for (k,v) in properties._fields_ 
        }
        return response
    raise Exception(f"Error getting properties for camera index {iCameraIndex}: "+str(res))

# ASICAMERA_API ASI_ERROR_CODE  ASIGetSerialNumber(int iCameraID, ASI_SN* pSN);
def ASIGetSerialNumber(iCameraID: int) -> str:
    _lib.ASIGetSerialNumber.restype = asi.AsiErrorCode
    pSN: ct.c_char_p
    res = _lib.ASIGetSerialNumber(iCameraID,pSN)
    if res == asi.AsiErrorCode.ASI_SUCCESS:
        return pSN.value#ct.cast(pSN, ct.c_char_p).value
    raise Exception(f"Error getting serial number for camera {iCameraID}: "+str(res))

#ASICAMERA_API ASI_ERROR_CODE  ASIStartExposure(int iCameraID, ASI_BOOL bIsDark);
def ASIStartExposure(iCameraID: int, isDark: asi.AsiBool):
    _lib.ASIStartExposure.restype = asi.AsiErrorCode
    res = _lib.ASIStartExposure(iCameraID, isDark.value)
    if res != asi.AsiErrorCode.ASI_SUCCESS:
        raise Exception(f"Error starting exposure (isDark={str(isDark)}) for camera {iCameraID}: "+str(res))

#ASICAMERA_API ASI_ERROR_CODE  ASIGetExpStatus(int iCameraID, ASI_EXPOSURE_STATUS *pExpStatus);
def ASIGetExpStatus(iCameraID: int):
    _lib.ASIGetExpStatus.restype = asi.AsiErrorCode
    buf = ct.c_int()
    res = _lib.ASIGetExpStatus(iCameraID, ct.byref(buf))
    if res == asi.AsiErrorCode.ASI_SUCCESS:
        return buf.value
    raise Exception(f"Error getting exposure status for camera {iCameraID}: "+str(res))

#ASICAMERA_API  ASI_ERROR_CODE ASIGetDataAfterExp(int iCameraID, unsigned char* pBuffer, long lBuffSize);
def ASIGetDataAfterExp(
    iCameraID: int,
    width: int,
    height: int,
    eightBit: bool
) -> np.array:

    _lib.ASIGetDataAfterExp.restype = asi.AsiErrorCode

    if eightBit:
        size = width*height
    else:
        size = width*height*2

    buf = (ct.c_ubyte*size)()
    res = _lib.ASIGetDataAfterExp(iCameraID, ct.byref(buf), size)
    #outputBitwidth = np.uint8 if eightBit else np.uint16 
    if res == asi.AsiErrorCode.ASI_SUCCESS:
        arr = np.ctypeslib.as_array(buf)
        if not eightBit:
            arr = np.ndarray((1,size//2),np.uint16, arr)
        #arr = np.ctypeslib.as_array(buf, (height, width)).astype(outputBitwidth).copy()
        return np.reshape(arr,(height,width)).copy()
    raise Exception(f"Error getting image after exposure for camera {iCameraID}: "+str(res))


# Not implemented yet

#ASICAMERA_API int ASIGetProductIDs(int* pPIDs);
#ASICAMERA_API ASI_BOOL ASICameraCheck(int iVID, int iPID);
#ASICAMERA_API ASI_ERROR_CODE ASIGetCameraPropertyByID(int iCameraID, ASI_CAMERA_INFO *pASICameraInfo);
#ASICAMERA_API ASI_ERROR_CODE ASIGetNumOfControls(int iCameraID, int * piNumberOfControls);
#ASICAMERA_API ASI_ERROR_CODE ASIGetControlCaps(int iCameraID, int iControlIndex, ASI_CONTROL_CAPS * pControlCaps);
#ASICAMERA_API  ASI_ERROR_CODE ASIGetROIFormat(int iCameraID, int *piWidth, int *piHeight,  int *piBin, ASI_IMG_TYPE *pImg_type); 
#ASICAMERA_API  ASI_ERROR_CODE ASISetStartPos(int iCameraID, int iStartX, int iStartY); 
#ASICAMERA_API  ASI_ERROR_CODE ASIGetStartPos(int iCameraID, int *piStartX, int *piStartY); 
#ASICAMERA_API  ASI_ERROR_CODE ASIGetDroppedFrames(int iCameraID,int *piDropFrames); 
#ASICAMERA_API ASI_ERROR_CODE ASIEnableDarkSubtract(int iCameraID, char *pcBMPPath);
#ASICAMERA_API ASI_ERROR_CODE ASIDisableDarkSubtract(int iCameraID);
#ASICAMERA_API  ASI_ERROR_CODE ASIStartVideoCapture(int iCameraID);
#ASICAMERA_API  ASI_ERROR_CODE ASIStopVideoCapture(int iCameraID);
#ASICAMERA_API  ASI_ERROR_CODE ASIGetVideoData(int iCameraID, unsigned char* pBuffer, long lBuffSize, int iWaitms);
#ASICAMERA_API  ASI_ERROR_CODE ASIGetVideoDataGPS(int iCameraID, unsigned char* pBuffer, long lBuffSize, int iWaitms, ASI_GPS_DATA *gpsData);
#ASICAMERA_API ASI_ERROR_CODE ASIPulseGuideOn(int iCameraID, ASI_GUIDE_DIRECTION direction);
#ASICAMERA_API ASI_ERROR_CODE ASIPulseGuideOff(int iCameraID, ASI_GUIDE_DIRECTION direction);
#ASICAMERA_API ASI_ERROR_CODE  ASIStopExposure(int iCameraID);
#ASICAMERA_API  ASI_ERROR_CODE ASIGetDataAfterExpGPS(int iCameraID, unsigned char* pBuffer, long lBuffSize, ASI_GPS_DATA *gpsData);
#ASICAMERA_API  ASI_ERROR_CODE ASIGetID(int iCameraID, ASI_ID* pID);
#ASICAMERA_API  ASI_ERROR_CODE ASISetID(int iCameraID, ASI_ID ID);
#ASICAMERA_API ASI_ERROR_CODE ASIGetGainOffset(int iCameraID, int *pOffset_HighestDR, int *pOffset_UnityGain, int *pGain_LowestRN, int *pOffset_LowestRN);
#ASICAMERA_API ASI_ERROR_CODE ASIGetLMHGainOffset(int iCameraID, int* pLGain, int* pMGain, int* pHGain, int* pHOffset);
#ASICAMERA_API char* ASIGetSDKVersion();
#ASICAMERA_API ASI_ERROR_CODE  ASIGetCameraSupportMode(int iCameraID, ASI_SUPPORTED_MODE* pSupportedMode);
#ASICAMERA_API ASI_ERROR_CODE  ASIGetCameraMode(int iCameraID, ASI_CAMERA_MODE* mode);
#ASICAMERA_API ASI_ERROR_CODE  ASISetCameraMode(int iCameraID, ASI_CAMERA_MODE mode);
#ASICAMERA_API ASI_ERROR_CODE  ASISendSoftTrigger(int iCameraID, ASI_BOOL bStart);
#ASICAMERA_API ASI_ERROR_CODE  ASISetTriggerOutputIOConf(int iCameraID, ASI_TRIG_OUTPUT_PIN pin, ASI_BOOL bPinHigh, long lDelay, long lDuration);
#ASICAMERA_API ASI_ERROR_CODE  ASIGetTriggerOutputIOConf(int iCameraID, ASI_TRIG_OUTPUT_PIN pin, ASI_BOOL *bPinHigh, long *lDelay, long *lDuration);
#ASICAMERA_API ASI_ERROR_CODE ASIGPSGetData(int iCameraID, ASI_GPS_DATA* startLineGPSData, ASI_GPS_DATA* endLineGPSData);
#ASICAMERA_API ASI_ERROR_CODE ASIEnableDebugLog(int iCameraID, ASI_BOOL bEnable);
#ASICAMERA_API ASI_ERROR_CODE ASIGetDebugLogIsEnabled(int iCameraID, ASI_BOOL *bEnable);
#ASICAMERA_API ASI_ERROR_CODE  ASISaveHPCTable(int iCameraID, unsigned char *table, long len);
#ASICAMERA_API ASI_ERROR_CODE  ASIHPCNumber(int iCameraID, int* piVal);
#ASICAMERA_API ASI_ERROR_CODE  ASIGetHPCTable(int iCameraID, unsigned char* table, long len);
#ASICAMERA_API ASI_ERROR_CODE  ASIEnableHPC(int iCameraID, ASI_BOOL bVal);
#ASICAMERA_API int ASIGetIDByIndex(int iCameraIndex);
#ASICAMERA_API ASI_ERROR_CODE  ASIEnableSnowTest(int iCameraID, ASI_BOOL bEnable);
#ASICAMERA_API ASI_ERROR_CODE  ASIWriteSonyReg(int iCameraID, unsigned short iAddr, unsigned char iValue);
#ASICAMERA_API ASI_ERROR_CODE  ASIReadFPGAReg(int iCameraID, unsigned short iAddr, unsigned char* piValue);
#ASICAMERA_API ASI_ERROR_CODE  ASIReadSpecialReg(int iCameraID, unsigned char iCmd, unsigned short iAddr, unsigned short* piValue);
#ASICAMERA_API int ASIGetPID(int iCameraID);
#ASICAMERA_API ASI_ERROR_CODE  ASIS50FilterSwitch(int iCameraID, int group, int val);
#ASICAMERA_API ASI_ERROR_CODE  ASIS50Heater(int iCameraID, ASI_BOOL bEnable);
#ASICAMERA_API ASI_ERROR_CODE  ASIS50RADECSensor(int iCameraID, ASI_BOOL* bRaEn, ASI_BOOL* bDecEn);
#ASICAMERA_API ASI_ERROR_CODE  ASISetTempControlValue(int iCameraID, int nTempSegment, int nHighTempDurationSec, int nLowTempDurationSec);
