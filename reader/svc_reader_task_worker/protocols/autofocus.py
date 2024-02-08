import sys
sys.path.insert(0, './common')
import base64
import cv2
import time
import numpy as np
import scipy.optimize
from artifactCodec import ArtifactCodec
codec = ArtifactCodec()

import log

logger = log.getLogger("reader_task_worker.autofocus")

argSchema = {
    'type': 'object',
    'properties': {
        'exposureDurationMs': {
            'type': 'number',
            'description': 'The exposure duration to be used for each of the images collected during the autofocus procedure. Measured in milliseconds.'
        },
        'binLevel': {
            'type': 'number',
            'description': 'The bin level to use for the auto focus procedure. Both X and Y bin will be set to this value.'
        },
        'sharpnessMeasure': {
            'type': 'string',
            'enum': ["gradient", "stdDev"],
            'description': 'Set the method for quantifying image sharpness. This is the function that will be maximized during autofocus. "gradient" is the default.'
        },
        'marginOfErrorUm': {
            'type': 'number',
            'description': 'The autofocus procedure will be accurate to within this distance. Default value is a "just noticeable difference" calculated based on reader geometry and optics.'
        },
        'nextSpanMethod': {
            'type': 'string',
            'enum': ['greatest', 'longest']
        }
    }
}

def getSharpnessStdDev(img):
    m, s = cv2.meanStdDev(img)
    return s[0][0]

def getSharpnessGradient(img):
    kernel_x = np.array([[1,0,-1],[1,0,-1],[1,0,-1]])
    kernel_y = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
    gradient_x = cv2.filter2D(img,cv2.CV_32F,kernel_x)
    gradient_y = cv2.filter2D(img,cv2.CV_32F,kernel_y)
    abs_gradient_x = np.absolute(gradient_x)
    abs_gradient_y = np.absolute(gradient_y)
    m, s = cv2.meanStdDev(abs_gradient_x + abs_gradient_y)
    return m[0][0]

def getGaussianStats(xs, ys):

    xs = np.array(xs)
    ys = np.array(ys)
    mean = sum(xs * ys) / len(xs)
    sigma = np.sqrt(sum(ys * (xs - mean)**2) / sum(ys))
    offset = (ys[0]+ys[1]) / 2

    def Gauss(x, a, x0, sigma, offset):
        return a * np.exp(-(x - x0)**2 / (2 * sigma**2)) - offset

    popt, _ = scipy.optimize.curve_fit(Gauss, xs, ys, p0=[max(ys), mean, sigma, offset])

    return popt[1], popt[2]

def computeJustNoticeableDifferenceZ(reader, binLevel):
    wavelength = reader['wavelength']
    aperature = reader['objectiveNumericalAperature']
    pixel_x = reader['sensorMicronsPerPixelX']
    pixel_y = reader['sensorMicronsPerPixelY']
    total_magnification = reader['totalMagnification']
    correction = reader['depthOfFieldCorrection']
    jndz =                                                        \
        correction                                                \
        *                                                         \
        (                                                         \
            (wavelength / aperature**2)                           \
            +                                                     \
            (                                                     \
                ((pixel_x + pixel_y) / 2)                         \
                *                                                 \
                (binLevel / (total_magnification * aperature))    \
            )                                                     \
        )
    return jndz

async def execute(ctx):
    camera = ctx['camera']
    board = ctx['board']
    args = ctx['args']

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

    def acquire(z, ms):
        board.setMotorZPositionUm(z)
        board.setLaserAOn(True)
        #this is awful, fix please!!!
        img = codec.tiffToArray(base64.b64decode(camera.exposeSync(ms).encode('ascii'))).astype(np.float32)
        board.setLaserAOn(False)
        return img

    def computeSpans(samples):
        samples = list(sorted(samples, key = lambda s: s[0]))
        spans = []
        for n in range(len(samples)-1):
            left = samples[n]
            right = samples[n+1]
            spans.append(
                {
                    'left_x': left[0],
                    'left_y': left[1],
                    'right_x': right[0],
                    'right_y': right[1],
                    'length': right[0] - left[0],
                    'avg_y': (left[1] + right[1])/2
                }
            )
        return spans

    connect_camera()

    zstage_limit_um = board.getMotorZLimitUm()
    
    sharpness_measure = args.get('sharpnessMeasure', 'gradient')
    exp_dur = args.get('exposureDurationMs', 100)
    bin_level = args.get('binLevel', 1)
    camera.setBin(bin_level, bin_level)
    jnd_z = computeJustNoticeableDifferenceZ(ctx['reader'], bin_level)
    margin_of_error = args.get('marginOfErrorUm', jnd_z)
    
    low_limit_z = 0
    high_limit_z = zstage_limit_um

    ideal_z = 0

    samples = []

    def sample(z):
        logger.info(f'Autofocus sampling at {z}')
        if sharpness_measure == 'stdDev':
            fz = getSharpnessStdDev
        else:
            fz = getSharpnessGradient
        samples.append((z, fz(acquire(z, exp_dur))))

    # sample at bottom, middle, and top
    sample(low_limit_z)
    sample((high_limit_z - low_limit_z) / 2)
    sample(high_limit_z)
    
    while True:
        # calculate all spans {leftsampxy, rightsampxy, length, avgy}
        spans = computeSpans(samples)

        # find highest sample
        highest_sample = max(samples, key = lambda s: s[1])

        logger.info(f'highest_sample={highest_sample}, all samples: {samples}')

        # find spans nearest highest sample whose length is greater than margin of error
        left_span = None
        right_span = None
        try:
            left_span = max(
                [
                    s for s in spans 
                    if s['right_x'] <= highest_sample[0]
                    and s['length'] > margin_of_error
                ],
                key = lambda s: s['right_x']
            )
        except ValueError:
            logger.info('no left span!')
        try:
            right_span = min(
                [
                    s for s in spans 
                    if s['left_x'] >= highest_sample[0]
                    and s['length'] > margin_of_error
                ],
                key = lambda s: s['left_x']
            )
        except ValueError:
            logger.info('no right span!')

        logger.info(f'left:{left_span}, right:{right_span}')

        # if both left and right spans are avaiable,
        # sample the one whose average value is greater
        if left_span and right_span:
            nextSpanMethod = args.get('nextSpanMethod', 'greatest')
            if nextSpanMethod == 'greatest':
                decide = lambda a,b: max(a,b, key=lambda x: x['avg_y'])
            elif nextSpanMethod == 'longest':
                decide = lambda a,b: max(a,b, key=lambda x: x['length'])

            next_span = decide(left_span, right_span)

        elif left_span or right_span:
            next_span = left_span or right_span
        else:
            logger.info('Sample space exhausted.')
            break

        logger.info(f'next_span:{next_span}')

        # calculate the next sample point in the middle of the desired span
        next_sample_z = next_span['left_x'] + ((next_span['right_x'] - next_span['left_x']) / 2)

        # take sample
        sample(next_sample_z)

        try:
            # update guess
            mean, sigma = getGaussianStats(*zip(*samples))
            new_ideal_z = mean

            # if the guess changed by a small enough amount, we're done
            # if not, keep sampling
            delta = abs(new_ideal_z - ideal_z)
            ideal_z = new_ideal_z
            logger.info(f'Delta Z on this round: {delta}')

            if delta < margin_of_error:
                break

        except RuntimeError:
            logger.info('Unable to fit curve, taking another sample')

    board.setMotorZPositionUm(ideal_z)
    logger.info(f'xs: {[x for x,y in samples]}, ys1: {[y for x,y in samples]}')
    logger.info(f'ideal z found! : {ideal_z}')

    
    return {
        'idealZ': ideal_z,
        'sampleCount': len(samples),
        'sampleStagePositions': [x for x,y in samples],
        'sampleSharpnessValues': [y for x,y in samples],
        'sharpnessMeasure': sharpness_measure,
        'binLevel': bin_level,
        'marginOfError': margin_of_error,
        'justNoticeableDifferenceZ': jnd_z
    }
