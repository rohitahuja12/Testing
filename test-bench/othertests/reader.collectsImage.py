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

logger = log.getLogger('test-bench.othertests.reader.collectsImage')
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

    readerSerialNumber = "reader123MOCK"
    readerMockBody = {
        "serialNumber": readerSerialNumber,
        "micronsPerMotorStep": {
            "x": 3.175,
            "y": 3.175,
            "z": 1
        },
        "cameraCenter": {
            "x": 45000, 
            "y": -8000
        },
        "cameraFovDims": {
            "x": 4000,
            "y": 4000
        },
        "defaultZ": 800,
        "mockImageTopLeft": {
            "x": 0,
            "y": 0
        },
        "mockImageBottomRight": {
            "x": 120000,
            "y": 400000
        }
    }
    with open('/phoenix/images/tiffsample.tif', 'rb') as f:
        readerMockImage = f.read()

    calibrationScanBody = {
        "name": "Test PHX Scan",
        "readerSerialNumber": readerSerialNumber,
        "productId": "calibrationPlate",
        "protocol": "calibrate",
        "status": "COMPLETE"
    }
    calibrationResults = {
        "cameraCenterCalibrated": {"x":10000,"y":10000}
    }
    productBody = {
        "productId": "testKit",
        "productDescription": {},
        "units": "microns",
        "exposures": [2500],
        "recommendedDilutionFactor": 1,
        "recommendedInitialConcentration": {},
        "features": [{
            "key": ["Well","A","12"],
            "region": [
                {"point":{"x":-10000,"y":-10000}},
                {"point":{"x":-15000,"y":-15000}}
            ]
        }]
    }
    imgName = "a12"
    scanBody = { 
        "name": "Test PHX Scan",
        "readerSerialNumber": readerSerialNumber,
        "productId": "testKit",
        "protocol": "pArray",
        "protocolArgs": {
            "images": [{
                "name": imgName,
                "region": [{"feature": ["Well","A","12"]}]
            }]
        }
    }

    async with ctx.dbDoc('readerMocks', readerMockBody) as r, ctx.dbDoc('products', productBody) as p, ctx.dbDoc('scans', calibrationScanBody) as cs, ctx.dbDoc('scans', scanBody) as s:

        checkpoint(True, 'Created a readerMock '+r['_id'])
        checkpoint(True, 'Created a product '+p['_id'])
        checkpoint(True, 'Created a calibration scan '+cs['_id'])
        checkpoint(True, 'Created a scan '+s['_id'])

        await db.createAttachment('readerMocks', r['_id'],
            readerMockImage, 'img')
        checkpoint(True, 'Attached img to readerMock')

        await db.createAttachment('scans', cs['_id'], 
            codec.dictToJson(calibrationResults), 'config')
        checkpoint(True, 'Created a calibration results attachment "config" on calibration scan '+cs['_id'])

        os.environ['MOCK_READER']=readerSerialNumber
        async with ctx.component('reader'):

            checkpoint(True, 'Started reader component, awaiting scan results')
            scanUpdates = db.getAllAndSubscribe('scans', {'_id':s['_id']})
            async for s in scanUpdates:
                checkpoint(True, str(s))
                if s['status'] == 'COMPLETE':
                    checkpoint(True, "Scan is completed.")
                    break
                elif s['status'] == 'ERROR':
                    checkpoint(False, "Scan ended in error status. "
                        + s.get('errorMessage',''))

        metas = await db.getAllAttachments('scans', s['_id'])
        checkpoint(True, "Attachment metadatas: "+str(metas))
        attachment = await db.getAttachment('scans', s['_id'], imgName)
        checkpoint(attachment, "Reader attaches image to scan")



