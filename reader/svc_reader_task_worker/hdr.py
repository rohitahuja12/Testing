import os
import ctypes as ct
import numpy as np
import itertools
from copy import deepcopy
import functools
from numpy.ctypeslib import ndpointer
import log
logger = log.getLogger("reader_task_worker.hdr")

'''
kwargs:
    mergeType = ['sum','debevec','robertson','mertens']
    preMergeTransform is a function that can be applied
        to each image before they are merged
'''
def hdrWithMetadata(expose, exposurems, **kwargs):

    metadata = {
        "exposures": []
    }
    imgs = []

    # rate at which exposures become shorter
    # where x is the index of the shot 
    getExposureDuration = lambda x: int(exposurems/pow(2,x))
    # getExposureDuration = lambda x: int(exposurems-(100*x))

    # The decreasing series of exposure durations
    exposureDurations = (getExposureDuration(x) for x in itertools.count(1))

    # How many ms must still be exposed to fill out
    # the desired exposure duration
    remainingExposure = exposurems

    # Exposure durations will decrease until one is found
    # which meets the criteria for 'non-saturated'.
    # This is the duration which first met this criteria.
    nonsaturatingExposure = 0

    # The pixel value, over which, a pixel will be considered
    # to be saturated.
    satValue = round(0.50 * np.iinfo(np.uint16).max)

    for exDuration in exposureDurations:

        metadata['exposures'].append(exDuration)
        img = expose(exDuration)
        imgs += [(img, exDuration)]

        totalPxls = img.shape[0] * img.shape[1]
        saturatedPxlCnt = np.count_nonzero(img >= satValue)

        remainingExposure -= exDuration
        if saturatedPxlCnt == 0:
            nonsaturatingExposure = exDuration
            break
    
    # expose remainder
    metadata['exposures'].append(remainingExposure)
    # logger.info(f'HDR exposures {metadata["exposures"]}')
    img = expose(remainingExposure)
    imgs += [(img,exDuration)]

    xform = kwargs.get('preMergeTransform', None)
    if xform:
        imgs = [(xform(i),dur) for (i,dur) in imgs]

    mergeType = kwargs.get('mergeType','sum')
    if mergeType == 'sum':
        result = hdrSum(imgs,satValue)
    return result

def hdrSum(imgs, satValue):
    # unpack images and durations
    imgList, durList = zip(*imgs)
    imgStack = np.stack(imgList).astype(ct.c_uint16)
    durs = np.stack(durList).astype(ct.c_int)
    #load the library
    phxHome = os.environ["PHOENIX_HOME"]
    libPath = os.path.join(phxHome, 'reader/svc_reader_task_worker/c_lib/hdrlib.so')
    _lib = ct.CDLL(libPath)

    _lib.hdr.restype = ct.c_int
    _lib.hdr.argtypes = [ndpointer(ct.c_uint16, flags="C_CONTIGUOUS"),
                        ct.c_int, ct.c_int, ct.c_int, 
                        ndpointer(ct.c_int, flags="C_CONTIGUOUS"), ct.c_int, 
                        ndpointer(ct.c_float, flags="C_CONTIGUOUS")]
    h,w = imgList[0].shape
    n = len(imgList)
    hdrImage = np.full(shape=(h,w), fill_value=0, dtype=ct.c_float)
    _lib.hdr(imgStack, w, h, n, durs, satValue, hdrImage)
    return hdrImage

def hdr(expose, exposurems, **kwargs):
    result = hdrWithMetadata(expose, exposurems, **kwargs)
    return result

