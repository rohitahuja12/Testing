import base64
import corrections 
import cv2
import imageLib
import io
import log
import math
import numpy as np
import scipy.optimize
import scipy.stats
import time
from artifactCodec import ArtifactCodec
from coords import Point, CoordTriplet
from functools import reduce
from hdr import hdr
from statistics import mean, stdev
from zipfile import ZipFile
from readerCacheHelper import storeCalibrationValue, storeCalibrationImage

codec = ArtifactCodec()
logger = log.getLogger('reader_task_worker.protocols.calibrate')


argSchema = {
    'type': 'object',
    'properties': {
        'saveComponentImages': {
            'type': 'boolean',
            'description': 'If set to true, some processes (darkImage, excitationNormalization e.g.) which use several component images to produce a calibration image will produce artifacts for each of those component images. This can be useful for debugging. Default: false.'
        },
        'skipDarkImage': {
            'type': 'boolean',
            'description': 'If set to true, the dark image procedure will not be run. No artifacts will be produced for this procedure. This can be useful for development. Default: false.'
        },
        'skipHotPixel': {
            'type': 'boolean',
            'description': 'If set to true, the hot pixel procedure will not be run. No artifacts will be produced for this procedure. This can be useful for development. Default: false.'
        },
        'skipExcitationNormalization': {
            'type': 'boolean',
            'description': 'If set to true, the excitation normalization procedure will not be run. No artifacts will be produced for this procedure. This can be useful for development. Default: false.'
        },
        'skipXYCalibration': {
            'type': 'boolean',
            'description': 'If set to true, the xy calibration procedure will not be run. No artifacts will be produced for this procedure. This can be useful for development. Default: false.'
        }
    }
}

def expose(ctx, millis):
    im = ctx['camera'].exposeSync(millis)
    im = base64.b64decode(im.encode('ascii'))
    im = codec.tiffToArray(im)
    im = im.astype(np.float32) 
    return im

async def execute(ctx):
    args = ctx['task']['protocolArgs']
    productId = ctx['task'].get('productId', args.get('productId'))
    product = await ctx['getProduct'](productId)
    ctx['locations'].setProduct(productId)
    ctx['board'].setIsAuxPowerOn(True)
    logger.info(f'Board power is ON: {ctx["board"].getIsAuxPowerOn()}')
    camera = ctx['camera']
    stage = ctx['stage']

    def connect_camera():
        #connect the camera 
        retryct = 10
        for retry in range(retryct):
            try:
                res = camera.connect()
                logger.info(f'connected camera! {res}')
                break
            except Exception as e:
                logger.error(f'Failed to connect camera {e}, retrying.')
                if retry < retryct:
                    time.sleep(1)
                else:
                    raise
    logger.info('going to connect camera...')
    connect_camera()

    # this will get called several times to add calibration values 
    # into the cache
    def populateCacheWithCalibrationValues(value_dict):
        for k,v in value_dict.items():
            storeCalibrationValue(k,v)


    # gather output files in here
    # zip and return from protocol
    resultImageFiles = {}

    # result values will get turned into a json doc before returning
    resultValues = {}

    binSettings = [1,3]

    ctx['board'].setRotatingDiffuserOn(True)

    try:
        twist = 0
        skew = 0
        if not args.get('skipTwistAndSkewCalibration', False):
            twist, skew, imgs = await calibrateStageTwistAndSkew(ctx)
            resultValues['stageTwist'] = twist
            resultValues['stageSkew'] = skew
            for count, img in enumerate(imgs):
                resultImageFiles[f'twist_skew_{count}'] = img
            logger.info(f'Found twist and skew to be {twist} and {skew} respectively.')

        populateCacheWithCalibrationValues(resultValues)

        if not args.get('skipXYCalibration', False):
            # disable xy offset correction (prior calibrations)
            ctx['locations'].setCorrectCalibratedXY(False)
            ctx['stage'].setCorrectTwist(True)
            xoffset, yoffset, imgs = await getXYOffset(ctx)
            resultValues['xoffset'] = xoffset
            resultValues['yoffset'] = yoffset
            for count, img in enumerate(imgs):
                resultImageFiles[f'xyoffset_{count}'] = img
            logger.info(f'Found XY offset to be {(xoffset, yoffset)}')

            populateCacheWithCalibrationValues(resultValues)
            # re-enable offset correction to test that corrections work
            ctx['locations'].setCorrectCalibratedXY(True)
            xoffset_postcorrection, yoffset_postcorrection, imgs_postcorrection = \
                await getXYOffset(ctx)
            for count, img in enumerate(imgs_postcorrection):
                resultImageFiles[f'xyoffset_postcorrection_{count}'] = img

            logger.info(f'After applying determining xyoffset and apply a correction, the new offset was found to be {xoffset_postcorrection}, {yoffset_postcorrection}')
            # assert abs(xoffset_postcorrection)<20 and abs(yoffset_postcorrection)<20


        populateCacheWithCalibrationValues(resultValues)

        for binSetting in binSettings:

            camera.setBin(binSetting, binSetting)

            if not args.get('skipDarkImage', False):
                
                darkImage, darkComponents = await getDarkImage(ctx)
                resultImageFiles[f'bin{binSetting}_darkImage'] = darkImage
                    
            if not args.get('skipHotPixel', False):

                hotPixelMask = await getHotPixelMask(ctx, darkImage)
                resultImageFiles[f'bin{binSetting}_hotPixelMask'] = hotPixelMask

            if not args.get('skipExcitationNormalization', False):

                normImage, normComponents = await getExcitationNormImage(
                        ctx, product, darkImage, hotPixelMask)
                resultImageFiles[f'bin{binSetting}_excitationNormImage'] = normImage

    finally:
        ctx['board'].setRotatingDiffuserOn(False)


    # populate the cache with the calibration images
    for k,v in resultImageFiles.items():
        storeCalibrationImage(k,v)

    resultFiles = {
        **{k:codec.arrayToTiff(v) for k,v in resultImageFiles.items()},
        'values.json': codec.dictToJson(resultValues)
    }
    await ctx['createArtifact'](resultFiles)

    return
    

async def getDarkImage(ctx):

    darkImgs = np.array([
        expose(ctx, 1)
        for _ in range(0,10)
    ])
    average = np.mean(darkImgs, axis=0)
    return average, darkImgs
    
async def getHotPixelMask(ctx, darkImage):
    logger.info('getting hot pixel mask!!!')

    # one long exposure, subtract dark
    img = expose(ctx, 10000)
    img = corrections.darkImageCorrector(darkImage)(img)

    # blank mask will be filled iteratively
    mask = np.zeros(img.shape, dtype=np.uint8)

    hotPixels = 0
    while True:

        avg = np.median(img)
        stddev = np.std(img)
        cutoff = avg+(8*stddev)

        isSaturated = lambda x: x == np.iinfo(np.uint16).max
        matricesOr = lambda *xs: reduce(lambda acc, x: np.logical_or(acc, x), xs)

        mask = np.where(
            matricesOr(mask, img>cutoff, isSaturated(img)), 
            255, 
            0
        ).astype(np.uint8)

        currHotPixels = np.count_nonzero(mask) 
        logger.info(f'GHPM: avg:{avg}, std:{stddev}, cutoff:{cutoff}, nhp:{currHotPixels-hotPixels}')
        if currHotPixels == hotPixels:
            break

        # apply mask to img, update count and try again
        img = np.where(mask==255, avg, img)
        hotPixels = currHotPixels

    return mask


async def getExcitationNormImage(ctx, product, darkImage, hotPixelMask):
    all_pts = ctx['locations'].getTopLevelPoints()
    norm_pts = [
        (p['x'],p['y']) 
        for p in all_pts 
        if "intensityPosition" in p['name'][0]
    ]

    camcenter = ctx['locations'].getPoint('cameraCenter')
    camx,camy = camcenter['x'], camcenter['y']

    logger.info(f'Board power is ON: {ctx["board"].getIsAuxPowerOn()}')
    imgs = []
    for ptx,pty in norm_pts:
        destx, desty = camx-ptx, camy-pty
        destz = ctx['reader']['defaultZ']
        ctx['stage'].move(destx, desty)
        ctx['board'].setMotorZPositionUm(destz)
        while ctx['stage'].get_state()['moving']:
            time.sleep(0.1)
        ctx['board'].setLaserAOn(True)
        img = expose(ctx, 500)
        ctx['board'].setLaserAOn(False)
        img = corrections.darkImageCorrector(darkImage)(img)
        imgs.append(img)

    def getAvg(xs):
        avg = mean(xs)
        #exclude one outlier pixel
        goods = sorted(xs, key=lambda x: np.abs(x-avg))
        return mean(goods[:-1])

    mergedImgs = cv2.merge(imgs)
    res = np.array([
        [getAvg(n) for n in row] 
        for row in mergedImgs
    ])
    # normalize
    res = res/np.mean(res) 
    
    return res, imgs
    

async def getXYOffset(ctx):

    sample_feature = ctx['args'].get('xyCalibrationFeature',"A01")
    sample_point = ctx['locations'].getPoint([sample_feature])
    cam_center = ctx['locations'].getPoint('cameraCenter')

    samplex, sampley = sample_point['x'], sample_point['y']
    camx, camy = cam_center['x'], cam_center['y'] 

    destx, desty = camx-samplex, camy-sampley

    ctx['stage'].move(destx, desty)
    while ctx['stage'].get_state()['moving']:
        time.sleep(0.1)

    ctx['board'].setMotorZPositionUm(600)

    ctx['board'].setLaserAOn(True)
    img = codec.tiffToArray(
            base64.b64decode(
                ctx['camera'].exposeSync(500).encode('ascii')
            )
        ).astype(np.float32)
    ctx['board'].setLaserAOn(False)

    spots = imageLib.findSpots(img, 10, 100, 10000)
    logger.info(spots)
    if len(spots) != 1:
        raise Exception(f"Unable to detect single spot, detected {len(spots)}")
    spot=spots[0]

    imageDimensionUm = ctx['reader']['objectiveFovDimsX']
    imageCenterPx = img.shape[1]//2, img.shape[0]//2
    umPerPx = imageDimensionUm / img.shape[0]
    xoffset = imageCenterPx[0] - spot['x']
    yoffset = imageCenterPx[1] - spot['y']

    (xoffset_um, yoffset_um) = (umPerPx * xoffset, umPerPx * yoffset)

    img = cv2.circle(img, (spot['x'],spot['y']), 10, 10000, 1)
    img = cv2.circle(img, (spot['x'],spot['y']), 11, 0, 1)

    return -xoffset_um, -yoffset_um, [img]
    

async def calibrateStageTwistAndSkew(ctx):

    def imageAtPoint(samplex, sampley):
        cam_center = ctx['locations'].getPoint('cameraCenter')
        camx, camy = cam_center['x'], cam_center['y'] 

        destx, desty = camx-samplex, camy-sampley

        ctx['stage'].move(destx, desty)
        while ctx['stage'].get_state()['moving']:
            time.sleep(0.1)

        ctx['board'].setMotorZPositionUm(600)

        ctx['board'].setLaserAOn(True)
        img = codec.tiffToArray(
                base64.b64decode(
                    ctx['camera'].exposeSync(500).encode('ascii')
                )
            ).astype(np.float32)
        ctx['board'].setLaserAOn(False)

        return img

    def getLineCenter(img, axis):

        def getGaussianStats(xs, ys):

            # logger.info(f'first 100 xs {xs[:100]}')
            # logger.info(f'first 100 ys {ys}')
            xs = np.array(xs)
            ys = np.array(ys)
            # mean = len(xs)//2
            mean = xs[list(ys).index(max(ys))]
            sigma = 10
            C = min(ys)

            def Gauss(x, a, x0, sigma, C):
                return a * np.exp(-(x - x0)**2 / (2 * sigma**2)) + C

            popt, _ = scipy.optimize.curve_fit(Gauss, xs, ys, p0=[max(ys), mean, sigma, C])

            logger.info(f'mean {popt[1]}, sigma {popt[2]}, C: {popt[3]}')
            return popt[1], popt[2]

        line = np.sum(img, axis)
        mean, sigma = getGaussianStats([x for x in range(len(line))], line)
        logger.info(f'Mean {mean}, sigma {sigma}')

        return round(mean)

    ctx['locations'].setCorrectCalibratedXY(False)
    ctx['stage'].setCorrectTwist(False)

    imageDimensionXUm = ctx['reader']['objectiveFovDimsX']
    imageDimensionYUm = ctx['reader']['objectiveFovDimsY']


    logger.info(f'Determining twist along X stage')

    # image at xtwist points 1 and 2 as specified in the instructions
    f1, f2 = ctx['args'].get('xTwistCalibrationFeatures', ["B01", "B12"])
    f1_loc = ctx['locations'].getPoint([f1])
    f2_loc = ctx['locations'].getPoint([f2])
    img_f1 = imageAtPoint(f1_loc['x'], f1_loc['y'])
    img_f2 = imageAtPoint(f2_loc['x'], f2_loc['y'])

    # find the density peaks in each image along X axis
    cntr_f1, cntr_f2 = getLineCenter(img_f1, 0), getLineCenter(img_f2, 0)
    logger.info(f'centers: {cntr_f1}, {cntr_f2}')
    
    # determine twist angle
    umPerPxX = imageDimensionXUm / img_f1.shape[0]
    umPerPxY = imageDimensionYUm / img_f1.shape[1]
    line_offset_um = (cntr_f2 - cntr_f1) * umPerPxX
    logger.info(f'Line offset microns: {line_offset_um}')
    stage_travel = (f2_loc['x'] - f1_loc['x'])
    logger.info(f'Stage travel: {stage_travel}')
    stage_twist_angle = np.arcsin(line_offset_um/stage_travel)


    logger.info(f'Determining twist along Y stage')

    # image at ytwist point 1, 2
    f3, f4 = ctx['args'].get('yTwistCalibrationFeatures', ["A02", "H02"])
    f3_loc = ctx['locations'].getPoint([f3])
    f4_loc = ctx['locations'].getPoint([f4])
    img_f3 = imageAtPoint(f3_loc['x'], f3_loc['y'])
    img_f4 = imageAtPoint(f4_loc['x'], f4_loc['y'])
    cntr_f3, cntr_f4 = getLineCenter(img_f3, 1), getLineCenter(img_f4, 1)
    logger.info(f'centers: {cntr_f3}, {cntr_f4}')
    
    line_offset_um = (cntr_f4 - cntr_f3) * umPerPxY
    logger.info(f'Line offset microns: {line_offset_um}')
    stage_travel = (f4_loc['y'] - f3_loc['y'])
    logger.info(f'Stage travel: {stage_travel}')
    stage_skew_angle = np.arcsin(-line_offset_um/stage_travel) - stage_twist_angle

    logger.info(f'stage twist angle: {stage_twist_angle}, {math.degrees(stage_twist_angle)}')
    logger.info(f'stage skew angle: {stage_skew_angle}, {math.degrees(stage_skew_angle)}')

    return -stage_twist_angle, -stage_skew_angle, [img_f1, img_f2, img_f3, img_f4]

async def testCameraAngle(ctx):
    pass

async def testReproducibilityXY(ctx):
    pass

async def testReproducibilityZ(ctx):
    pass
