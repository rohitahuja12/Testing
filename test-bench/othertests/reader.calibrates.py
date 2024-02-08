import os
import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 
import uuid
import shutil
import log
import json
import imageio
from artifactCodec import ArtifactCodec
codec = ArtifactCodec()

logger = log.getLogger('test-bench.othertests.reader.calibrates')
requiredComponents = ['db','resource-api']

async def execute(checkpoint):


    # point: x y
    # region: [point]
    # feature: [point|region|feature]

    # sum: (x:region|feature) -> [point] -> x -> x

    # movetocamera: 

    # to build a shot
    # resolve features/regions into points
    # draw the smallest fit box around those points
    # decide how many subshots are required
    # calculate the center points of those shots
    # move those points over the camera in sequence
    # take pictures
    # stitch together
    # label points/regions/features used to define shot in output?

    readerBody = {
        "serialNumber": "reader123MOCK",
        "micronsPerXYMotorStep": 3.175,
        "cameraCenterApprox": {
            
        }
    }
    productBody = {
        "productId": "calibrationPlate",
        "productDescription": {},
        "units": "microns",
        "exposures": [3500],
        "recommendedDilutionFactor": 1,
        "recommendedInitialConcentration": {},
        "features": [{
            "key": ["Well", "A", "12"],
            "region": [{"point": {"x": -11050, "y": -14270}}]
        }]
    }
    scanBody = {
        "name": "Test PHX Scan",
        "readerSerialNumber": readerBody['serialNumber'],
        "productId": "calibrationPlate",
        "protocol": "calibrate"
    }

    # async with ctx.component('db'), ctx.component('resource-api'), ctx.component('reader'):

    async with ctx.dbDoc('readers', readerBody) as r, ctx.dbDoc('products', productBody) as p, ctx.dbDoc('scans', scanBody) as s:

        checkpoint(True, 'Created a calibration scan '+s['_id'])

        os.environ['MOCK_READER']="True"
        async with ctx.component('reader'):

            scanUpdates = db.getAllAndSubscribe('scans', {'_id':s['_id']})
            async for s in scanUpdates:
                checkpoint(True, str(s))

