import sys
sys.path.insert(0, './common')
# test only
sys.path.insert(0, './reader/reader_task_worker')
# end test only
import base64
import coords
import corrections
import cv2
from datetime import datetime as dt
import log
import eventLogging
import numpy as np
import plotting as plot
import readerCacheHelper
import json
import time
import utils
from artifactCodec import ArtifactCodec
from hdr import hdrWithMetadata
from spot_intensity_detector.detector import ImageAcqDetails, SpotAcqDetails
logger = log.getLogger("reader_task_worker.pArray")
event = eventLogging.get_event_logger(logger)
codec = ArtifactCodec()

argSchema = {
    'type': 'object',
    'properties': {}
}

async def execute(ctx):
    event("EVENT_PARRAY_START")
    # services
    stage = ctx['stage']
    board = ctx['board']
    camera = ctx['camera']
    locations = ctx['locations']
    cache = ctx['cache']

    def connect_camera():
        #connect the camera 
        retryct = 10
        for retry in range(retryct):
            try:
                camera.connect()
                break
            except Exception as e:
                if retry < retryct:
                    time.sleep(1)
                else:
                    raise e
    connect_camera()

    # callbacks
    getTaskArtifact = ctx['getTaskArtifact']
    getProduct = ctx['getProduct']

    # data
    task = ctx['task']
    reader = ctx['reader']
    args = ctx['args']

    product = await getProduct(ctx['task']['productId'])

    microArray = product["relativeFeatures"]["microArray"]
    microArraySpotDict = microArray["features"]

    logger.info(f'setting product to {product["_id"]}')
    locations.setProduct(product['_id'])

    roi_um_x = reader['objectiveFovDimsX']
    roi_um_y = reader['objectiveFovDimsY']

    # gather output files in here
    # zip and return from protocol
    results = {}

    localCalibrationCache = {}
    def calibrationImageGetter(binSetting, name):
        key = f'bin{binSetting}_{name}'
        if localCalibrationCache.get(key, None) is None:
            localCalibrationCache[key] = readerCacheHelper.getCalibrationImage(key)
        return localCalibrationCache[key]

    # This is important becuase the first frame is garbo
    camera.exposeSync(1)

    try:
        imageMetadatas = []
        for index, image in enumerate(args['images']):

            def lookupSetting (name, defaultit):
                return image.get(name, 
                    args.get(name, 
                        product.get(name, 
                            reader.get(name, 
                                defaultit))))

            imageResultName = image.get('name', 'img'+str(index))
            logger.info('Creating image '+str(image))

            fName = image['region'][0]['feature']
            featureName = ''.join([fName[1],fName[2].zfill(2)]) # produces "A01", for example
            logger.info(f'retrieving location of feature {featureName}')
            imageCenter = locations.getPoint([featureName])
            camCenter = locations.getPoint("cameraCenter")

            destx = camCenter['x'] - imageCenter['x']
            desty = camCenter['y'] - imageCenter['y']
            stage.move(destx,desty)
            # ensure the stage has reached its destination before continuing
            while stage.get_state()['moving']:
                time.sleep(0.1)

            # perform autofocus on this well if specified
            if lookupSetting('autofocus', False):
                af_result = await ctx['protocols']['autofocus']['module'].execute(ctx)
            else:
                destz = image.get('defaultZ', ctx['reader']['defaultZ'])
                logger.info(f'moving to: {(destx, desty, destz)}')
                board.setMotorZPositionUm(destz)

            binX = lookupSetting('cameraBinX', 1)
            binY = lookupSetting('cameraBinY', 1)
            assert binX==binY
            binSetting = binX
            camera.setBin(binSetting, binSetting)

            logger.info('exposing...')
            def buildExpose(hdr, correctDark, correctHotPixel, correctNorm):
                expose = utils.compose(
                    lambda im: im.astype(np.float32),
                    codec.tiffToArray,
                    lambda im: base64.b64decode(im.encode('ascii')),
                    camera.exposeSync
                )

                if correctHotPixel:
                    expose = utils.compose(
                        corrections.hotPixelCorrector(
                            calibrationImageGetter(binSetting, 'hotPixelMask')
                        ), 
                        expose
                    )

                if hdr:
                    xform = corrections.darkImageCorrector(calibrationImageGetter(binSetting, 'darkImage')) \
                            if correctDark \
                            else lambda x: x
                    # do this becuase python scoping sucks
                    exOld = expose
                    expose = lambda ms: hdrWithMetadata(exOld, ms, mergeType='sum', preMergeTransform=xform)

                # elif because this correction gets applied during HDR if it is on
                elif correctDark:
                    expose = utils.compose(
                        corrections.darkImageCorrector(
                            calibrationImageGetter(binSetting, 'darkImage')
                        ), 
                        expose
                    )

                if correctNorm:
                    expose = utils.compose(
                        corrections.excitationNormCorrector(
                            calibrationImageGetter(binSetting, 'excitationNormImage')
                        ), 
                        expose
                    )

                return expose

            expose = buildExpose(
                lookupSetting('hdr', True),
                lookupSetting('darkImageCorrection', True),
                lookupSetting('hotPixelCorrection', True),
                lookupSetting('excitationNormCorrection', True)
            )

            rotateDiffuser = lookupSetting('rotateDiffuser', True)
            if board.getRotatingDiffuserOn() != rotateDiffuser:
                board.setRotatingDiffuserOn(rotateDiffuser)

            laserOn = lookupSetting('laserOn', True)
            if laserOn:
                logger.info('lasering...')
                board.setLaserAOn(True)

            exposure = lookupSetting('exposures', None)[0]
            logger.info(f'looked up exposure at {exposure}')
            resultImg = expose(exposure)
            logger.info(f'exposure complete')

            if laserOn:
                board.setLaserAOn(False)

            # convert to 8bit if specified
            if lookupSetting('lowResOutput', False):
                resultImg = cv2.normalize(
                    resultImg, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)


            results[imageResultName] = codec.arrayToTiff(resultImg)
            logger.info(f'encoded image as tiff')

            # create a list of spot pixel locations for metadata
            def get_image_acq_details():
                microarray_center = locations.getPoint([featureName])
                im_width_px = resultImg.shape[0]
                im_height_px = resultImg.shape[1]
                im_top_left_px_x = int(microarray_center['x_px']-im_width_px/2)
                im_top_left_px_y = int(microarray_center['y_px']-im_height_px/2)

                spot_locs_px = locations.getChildPoints([featureName, 'microArray'])
                spot_locs_px = {s['name'][-1]:(s['x_px'],s['y_px']) for s in spot_locs_px}

                stage_pos = stage.getPosUm()

                imageMeta = ImageAcqDetails(
                    time=dt.utcnow().isoformat(),
                    fovSizeXUm=roi_um_x,
                    fovSizeYUm=roi_um_y,
                    zStagePositionUm=board.getMotorZPositionUm(),
                    xStagePositionUm=stage_pos[0],
                    yStagePositionUm=stage_pos[1],
                    imageName=imageResultName,
                    spots=[
                        SpotAcqDetails(
                            analyte=v['attrs']['analyte'],
                            row=v['attrs']['row'],
                            column=v['attrs']['col'],
                            x_px=spot_locs_px[k][0]-im_top_left_px_x,
                            y_px=spot_locs_px[k][1]-im_top_left_px_y
                        )
                        for k,v in microArraySpotDict.items()
                    ]
                )

                # START dev plot thing
                # im_btm_right_px_x = int(microarray_center['x_px']+im_width_px/2)
                # im_btm_right_px_y = int(microarray_center['y_px']+im_height_px/2)
                # pxplot = plot.plot([
                    # plot.XYScalesEqual(),
                    # plot.XIncreasesLTR(),
                    # plot.YIncreasesTTB(),
                    # plot.Point(coords.Point(im_top_left_px_x, im_top_left_px_y), "top left"),
                    # plot.Point(coords.Point(im_btm_right_px_x, im_btm_right_px_y), "btm right"),
                    # *[
                        # plot.Point(coords.Point(p[0], p[1]), 'pt')
                        # for p in spot_locs_px.values()
                    # ]
                # ])
                # results[f'spotplotpx{featureName}'] = pxplot
                # END end dev plot

                return imageMeta

            imageMetadatas.append(get_image_acq_details().to_dict())
            logger.info(f'recorded image acquisition details')
            results["imageMetadata.json"]=codec.dictToJson({"metadata":imageMetadatas})
            logger.info(f'encoded imageMetadata as JSON file')

        await ctx['createArtifact'](results)
        logger.info(f'enqueued artifact')

    finally:
        board.setRotatingDiffuserOn(False)

