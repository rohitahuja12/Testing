# This file loads the .so file
# Hides all ctypes details from calling code
import ArtemisTypes as at
import typing
import os
import subprocess
import asyncio
import ctypes as ct
import numpy as np
import log
logger = log.getLogger('controller_camera.atik_infinity_client')
import pyudev



#_lib = ct.cdll.LoadLibrary('/usr/local/lib/libatikcameras.so')
phxHome = os.environ["PHOENIX_HOME"]
libPath = os.path.join(phxHome, 'reader/svc_controller_camera/libatikcameras.so')

_lib = ct.CDLL(libPath)

'''
---------- dll ----------
'''

# def ArtemisAllowDebugToConsole(value: bool):
    # return _lib.ArtemisAllowDebugToConsole(value)

def ArtemisShutdown():
    return _lib.ArtemisShutdown()

'''
---------- Device ----------
'''

def ArtemisRefreshDevicesCount():
    return _lib.ArtemisRefreshDevicesCount()

def ArtemisDeviceCount():
    return _lib.ArtemisDeviceCount()

def ArtemisDevicePresent(iDevice: int) -> bool:
    return _lib.ArtemisDevicePresent(iDevice)

def ArtemisDeviceInUse(iDevice: int) -> bool:
    return _lib.ArtemisDeviceInUse(iDevice)

def ArtemisConnect(iDevice: int) -> at.ArtemisHandle:
    return _lib.ArtemisConnect(iDevice)

def ArtemisIsConnected(handle: at.ArtemisHandle):
    return _lib.ArtemisIsConnected(handle)

def ArtemisDisconnect(handle: at.ArtemisHandle):
    return _lib.ArtemisDisconnect(handle)

'''
---------- Camera Info ----------
'''
def ArtemisProperties(handle: at.ArtemisHandle):
    properties = at.ArtemisProperties()
    _lib.ArtemisProperties.restype = at.ArtemisError

    res = _lib.ArtemisProperties(handle, ct.byref(properties))
    def toString(x):
        return x.decode('ascii') if isinstance(x, typing.ByteString) else x
    if res == at.ArtemisError.ARTEMIS_OK:
        # return properties
        response = { 
            k: toString(getattr(properties, k))
            for (k,v) in properties._fields_ 
        }
        return response
    raise Exception("Error getting properties "+str(res))

def ArtemisDeviceName(handle: at.ArtemisHandle):
    out = ct.c_char()
    _lib.ArtemisDeviceName(handle, ct.byref(out))

    return out.value.decode('ascii')

def ArtemisDeviceSerial(handle: at.ArtemisHandle):
    out = ct.c_char()
    _lib.ArtemisDeviceSerial(handle, ct.byref(out))

    return out.value.decode('ascii')



'''
---------- Exposure Settings ----------
'''

def ArtemisBin(handle: at.ArtemisHandle, x: int, y:int):
    return _lib.ArtemisBin(handle, x, y)

def ArtemisGetBin(handle: at.ArtemisHandle):
    x = ct.c_int()
    y = ct.c_int()
    _lib.ArtemisGetBin.restype = at.ArtemisError
    
    res = _lib.ArtemisGetBin(handle, ct.byref(x), ct.byref(y))

    if res == at.ArtemisError.ARTEMIS_OK:
        return {"x":x.value, "y":y.value}

    raise Exception("Error getting bin values: "+str(res))

def ArtemisEightBitMode(handle: at.ArtemisHandle, eightBitMode: bool):
    return _lib.ArtemisEightBitMode(handle, eightBitMode)

def ArtemisGetEightBitMode(handle: at.ArtemisHandle):
    eightBit = ct.c_bool()
    _lib.ArtemisGetEightBitMode.restype = at.ArtemisError

    res = _lib.ArtemisGetEightBitMode(handle, ct.byref(eightBit))

    if res == at.ArtemisError.ARTEMIS_OK:
        return eightBit.value

    raise Exception("Error getting eight bit mode: "+str(res))

'''
---------- Exposures ----------
'''

def ArtemisStartExposureMS(
    handle: at.ArtemisHandle, 
    millis: int
) -> None:
    _lib.ArtemisStartExposureMS.restype = at.ArtemisError
    res = _lib.ArtemisStartExposureMS(handle, ct.c_int(millis))
    if res == at.ArtemisError.ARTEMIS_OK:
        return None
    raise Exception("Error starting exposure: "+str(res))

def ArtemisCameraState(handle: at.ArtemisHandle):
    _lib.ArtemisCameraState.restype = at.ArtemisCameraState
    return _lib.ArtemisCameraState(handle)

def ArtemisDownloadPercent(handle: at.ArtemisHandle):
    return _lib.ArtemisDownloadPercent(handle)

def ArtemisImageReady(
    handle: at.ArtemisHandle
) -> bool:
    return _lib.ArtemisImageReady(handle)

def ArtemisGetImageData(
    handle: at.ArtemisHandle
) -> (int, int, int, int, int, int):

    w = ct.c_int()
    h = ct.c_int()
    x = ct.c_int()
    y = ct.c_int()
    xBin = ct.c_int()
    yBin = ct.c_int()

    _lib.ArtemisGetImageData.restype = at.ArtemisError
    res = _lib.ArtemisGetImageData(handle, ct.byref(x), ct.byref(y), 
        ct.byref(w), ct.byref(h), ct.byref(xBin), ct.byref(yBin))
    if res == at.ArtemisError.ARTEMIS_OK:
        return {
            "width":w.value, 
            "height":h.value, 
            "x": x.value, 
            "y": y.value, 
            "xBin": xBin.value, 
            "yBin": yBin.value
        }
    else:
        raise Exception("Error in ArtemisGetImageData: "+str(res))

def ArtemisImageBuffer(
    handle: at.ArtemisHandle, 
    width: int, 
    height: int,
    eightBit: bool
) -> np.array:

    # buffer bitwidth is always 16bit, even when camera is in 8bit mode
    _lib.ArtemisImageBuffer.restype = ct.POINTER(ct.c_int16)
    outputBitwidth = np.uint8 if eightBit else np.uint16 
    buf = _lib.ArtemisImageBuffer(handle)
    arr = np.ctypeslib.as_array(buf, (height, width)).astype(outputBitwidth).copy()

    return arr

