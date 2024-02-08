import sys
sys.path.insert(0, './common')
# test only
sys.path.insert(0, './reader/reader_task_worker')
# end test only
import base64
import coords
import corrections
import cv2
import itertools
import json
import log
import numpy as np
import plotting as plot
import readerCacheHelper
import utils
import spot_intensity_detector.detector as detector
import time
from artifactCodec import ArtifactCodec
from functools import reduce
from hdr import hdrWithMetadata
from regionHelper import regions
logger = log.getLogger("reader_task_worker.pArray")
codec = ArtifactCodec()

argSchema = {
    'type': 'object',
    'properties': {}
}

async def execute(ctx):
    # services
    stage = ctx['stage']
    board = ctx['board']
    camera = ctx['camera']
    locations = ctx['locations']

    # callbacks
    getTaskArtifact = ctx['getTaskArtifact']
    getProduct = ctx['getProduct']

    # data
    task = ctx['task']
    reader = ctx['reader']
    args = task['protocolArgs']

    product = await getProduct(ctx['task']['productId'])

    roi_um_x = reader['objectiveFovDimsX']
    roi_um_y = reader['objectiveFovDimsY']

    # gather output files in here
    # zip and return from protocol
    results = {}

    darkImage, hotPixelMask, excitationNormImage = await loadCalibrationImages(
        reader['serialNumber'],
        getTaskArtifact)

    locations.setProduct(product['_id'])

    imageMetadatas = {}
    images = []
    image_top_lefts_um = []
    image_bottom_rights_um = []
    image_spot_locations_um = []
    for index, image in enumerate(args['images']):

        imageMeta = {
            "sizex": roi_um_x, 
            "sizey": roi_um_y
        }
        imageResultName = image.get('name', 'img'+str(index))
        logger.info('Creating image '+str(image))

        fName = image['region'][0]['feature']
        featureName = ''.join([fName[1],fName[2].zfill(2)]) # produces "A01", for example
        imageCenter = locations.getPoint([featureName])
        camCenter = locations.getPoint("cameraCenter")

        destx = camCenter['x'] - imageCenter['x']
        desty = camCenter['y'] - imageCenter['y']
        destz = image.get('defaultZ', ctx['reader']['defaultZ'])
        logger.info(f'moving to: {(destx, desty, destz)}')
        stage.setPosUm(destx,desty)

        # block until stopped
        while stage.isMoving():
            time.sleep(0.1)

        board.setMotorZPositionUm(destz)

        def lookupSetting (name, defaultit):
            return image.get(name, args.get(name, product.get(name, defaultit)))

        laserOn = lookupSetting('laserOn', True)
        if laserOn:
            logger.info('lasering...')
            board.setLaserAOn(True)

        logger.info('exposing...')
        exposure = product['exposures'][0]

        expose = utils.compose(lambda x: base64.b64decode(x.encode('ascii')), camera.exposeSync)
        expose = utils.compose(codec.tiffToArray, expose)

        if lookupSetting('hotPixelCorrection', True):
            logger.info(f'correcting hp')
            expose = utils.compose(corrections.hotPixelCorrector(hotPixelMask), expose)

        if lookupSetting('hdr', True):
            logger.info(f'performing hdr')
            if lookupSetting('darkImageCorrection', True):
                xform = corrections.darkImageCorrector(darkImage) \
                        if lookupSetting('darkImageCorrection', True) \
                        else lambda x: x
            # do this becuase python scoping sucks
            exOld = expose
            expose = lambda ms: hdrWithMetadata(exOld, ms, mergeType='sum', preMergeTransform=xform)

        # elif because this correction gets applied during HDR if it is on
        elif lookupSetting('darkImageCorrection', True):
            logger.info(f'correcting dark')
            expose = utils.compose(corrections.darkImageCorrector(darkImage), expose)

        if lookupSetting('excitationNormCorrection', True):
            logger.info(f'correcting excitation')
            expose = utils.compose(corrections.excitationNormCorrector(excitationNormImage), expose)

        resultImg = expose(exposure)
        
        if laserOn:
            board.setLaserAOn(False)

        # convert to 8bit if specified
        if lookupSetting('lowResOutput', False):
            resultImg = cv2.normalize(
                resultImg, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

        # get data ready for intensity calculation
        images.append(resultImg)
        image_top_lefts_um.append((imageCenter['x']-roi_um_x, imageCenter['y']-roi_um_y))
        image_bottom_rights_um.append((imageCenter['x']+roi_um_x, imageCenter['y']+roi_um_y))
        spots = locations.getChildPoints([featureName,'microArray'])
        spots = [(spot['x'],spot['y'],spot['name'][-1]) for spot in spots]
        image_spot_locations_um.extend(spots)
        results[imageResultName] = codec.arrayToTiff(resultImg)
        imageMetadatas[imageResultName] = imageMeta

    intensities = detector.detect_intensities(
        images, 
        image_top_lefts_um, 
        image_bottom_rights_um, 
        image_spot_locations_um, 
        500)
    intensities = [(*i[:-1],float(i[-1])) for i in intensities]

    results["intensities.json"]=codec.dictToJson({'intensities':intensities})
    results["imageMetadata.json"]=codec.dictToJson(imageMetadatas)

    intensityList = produceIntensityList(args['images'], images)
    return results


async def loadCalibrationImages(readerSerialNumber, getTaskArtifact):
    calScan = await readerCacheHelper.getMostRecentCalibrationScan(readerSerialNumber)

    darkImage = await getTaskArtifact(calScan['_id'], 'darkImage')
    darkImage = codec.tiffToArray(darkImage).astype(np.float32)

    hotPixelMask = await getTaskArtifact(calScan['_id'], 'hotPixelMask')
    hotPixelMask = codec.tiffToArray(hotPixelMask).astype(np.uint8)

    excitationNormImage = await getTaskArtifact(calScan['_id'], 'excitationNormImage')
    excitationNormImage = codec.tiffToArray(excitationNormImage).astype(np.float32)

    return darkImage, hotPixelMask, excitationNormImage


def produceIntensityList(imageInstructions, images):
    # this is just debug code to write out data to use for tests later.
    for index, image in enumerate(images):
        with open(f'/phoenix/reader/logs/images/run0/i{index}.tif', 'wb') as f:
            f.write(codec.arrayToTiff(image))
    with open(f'/phoenix/reader/logs/images/run0/instructions.json', 'w') as f:
        f.write(json.dumps(imageInstructions))
    
