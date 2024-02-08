import sys
import base64
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import lib_hardware_interface.client as hwclient
import log
import os
import numpy as np
import artifactCodec

logger = log.getLogger("common.readerCacheHelper")
cacheRequestTransport = os.environ['READER_CACHE_REQUEST_TRANSPORT']

def getCache():
    return hwclient.HardwareClient(cacheRequestTransport)

async def getEncodedCachedValueOrRunFetch(key: str, fetch = None, encoder = None, decoder = None):
    cache = getCache()
    value = cache.getCachedValue(key)

    if value == "":
        value = None
    if value is None and fetch is not None:
        value = await fetch()
        if encoder is not None:
            cache.cacheValue(key, encoder(value))
        else:
            cache.cacheValue(key, value)
    else:
        if decoder is not None:
            value = decoder(value)

    return value

cache = getCache()
codec = artifactCodec.ArtifactCodec()

def storeCalibrationValue(key, value):
    return cache.cacheValue(f'calibration_{key}', value)

def getCalibrationValue(key):
    val = cache.getCachedValue(f'calibration_{key}')
    return val

def storeCalibrationImage(key, array_data):
    image_data = codec.arrayToTiff(array_data)
    data_string = base64.b64encode(image_data).decode('ascii')
    return cache.cacheValue(f'calibration_image_{key}', data_string)

def getCalibrationImage(key):
    data_string = cache.getCachedValue(f'calibration_image_{key}')
    image_data = base64.b64decode(data_string.encode('ascii'))
    array_data = codec.tiffToArray(image_data).astype(np.float32)
    return array_data

