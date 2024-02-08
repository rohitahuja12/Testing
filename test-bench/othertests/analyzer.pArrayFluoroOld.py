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
import dataGenerators.scanImageGenerator as imgGen

logger = log.getLogger('test-bench.othertests.analyzer.pArrayFluoroOld')

tags = ['db','mock-reader']
requiredComponents = ['db','resource-api','mock-reader','analyzer']

async def execute(checkpoint):

    logger.info("Running array test bench test...")
    testImage = imgGen.createArrayTestImage(341,341,80)
    logger.info(str("Test image type: "+str(type(testImage)) ))

    readerId = "reader-"+str(uuid.uuid4())
    scanBody = { 
        "name": "My scan!",
        "readerId": readerId,
        "protocol": "pSpotFluoro",
        "protocolArgs": {},
        "volumeStorage": True,
        "productId": "kit1",
        "configIds": []
    }
    os.environ['MOCK_READER_ATTACHMENT_PATHS'] = '/testbenchstuff/images/pFluoro.tif'
    os.environ['MOCK_READER_ID'] = readerId

    if not os.path.exists('/testbenchstuff/images'):
        os.makedirs('/testbenchstuff/images')

    if not os.path.exists('./testbenchstuff/images/pFluoro.tif'):
        shutil.copyfile(
            '/phoenix/images/pFluoro.tif', 
            '/testbenchstuff/images/pFluoro.tif')

    async with ctx.dbDoc('readers', {"serialNumber": readerId}) as r, ctx.dbDoc('scans', scanBody) as s:

        checkpoint(True, 'Created a scan '+s['_id'])

        analysisBody = {
            "name": "Test PFluoro analysis",
            "protocol": "pSpotFluoro",
            "protocolArgs": {
                "minSpotDiameter": 3,
                "maxSpotDiameter": 10,
                "threshold": 1000
            },
            "scanId": s['_id']
        }

        docs = db.getAllAndSubscribe('scans')
        running = False
        async for doc in docs:
            if doc['_id'] != s['_id']:
                continue
            if doc['status'] == 'RUNNING':
                # only pass checkpoint the first time, other changes will come through
                # for each attachment the analyzer posts.
                if not running:
                    checkpoint(True, 'MockReader updates scan to "RUNNING"')
                    running = True
            elif doc['status'] == 'COMPLETE':
                checkpoint(True, 'MockReader updates scan to "COMPLETE"')
                break
                

        async with ctx.dbDoc('analyses', analysisBody) as a:

            checkpoint(True, 'Created an analysis '+a['_id'])
            
            changes = db.getAllAndSubscribe('analyses')
            running = False
            async for doc in changes:
                if doc['_id'] != a['_id']:
                    continue
                if doc['status'] == 'RUNNING':
                    # only pass checkpoint the first time, other changes will come through
                    # for each attachment the analyzer posts.
                    if not running:
                        checkpoint(True, 'Analyzer updates analysis to "RUNNING"')
                        running = True
                elif doc['status'] == 'COMPLETE':
                    checkpoint(True, 'Analyzer updates analysis to "COMPLETE"')
                    break
                elif doc['status'] == 'ERROR':

                    checkpoint(False, 'Analyzer finished with errors:' + ','.join(doc['errors']))
                    break
            imageOutput=await db.getAllAttachments("analyses",a['_id'])
            logger.info(str(imageOutput) )
            attFb =  await db.getAttachment("analyses",a['_id'],"maxima1.jpg")
            with open("/phoenix/test-data-output/maxima1.jpg","wb") as f:
                f.write(attFb)

            with open("/phoenix/test-data-input/scan.json") as f:
                result = json.load(f)

            logger.info("Scan json file: "+str(result))


