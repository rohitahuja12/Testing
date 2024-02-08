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
logger = log.getLogger('test-bench.othertests.mockReader.happyPath')

tags = ['db','mock-reader']
requiredComponents = ['db','resource-api','mock-reader','analyzer']

async def execute(checkpoint):

    readerSerialNumber = "reader-"+str(uuid.uuid4())
    scanBody = { 
        "name": "My scan!",
        "readerSerialNumber": readerSerialNumber,
        "protocol": "pSpotFluoro",
        "protocolArgs": {},
        "productId": "kit1",
        "configIds": []
    }
    os.environ['MOCK_READER_ATTACHMENT_PATHS'] = '/testbenchstuff/images/tiffsample.tif'
    os.environ['MOCK_READER_ID'] = readerSerialNumber

    # move image into volume
    if not os.path.exists('/testbenchstuff/images'):
        os.makedirs('/testbenchstuff/images')

    shutil.copyfile(
        '/phoenix/images/tiffsample.tif', 
        '/testbenchstuff/images/tiffsample.tif')

    # async with ctx.component('db'), ctx.component('resource-api'), ctx.component('mock-reader'), ctx.component('analyzer'):

    scanId = None
    scan = None
    async def listenForScanChanges():
        # subscribe to everything because we don't know the id of the scan yet
        #{'ns':{'db':'reader','coll':'scans'}}
        changes = db.getAllAndSubscribe('scans')
        async for doc in changes:
            # if the item lacks 'fullDocument' or if the item has 'fullDocument' and the id is not our scan, skip it
            if doc['_id'] != scanId:
                continue
            if doc['status'] == 'RUNNING':
                checkpoint(True, 'Mock-reader updates scan status to "RUNNING"')
            elif doc['status'] == 'COMPLETE':
                checkpoint(True, 'Mock-reader updates scan status to "COMPLETE"')
                break
            elif doc['status'] == 'ERROR':
                checkpoint(False, 'Mock-reader finished with errors:' + ','.join(doc['errors']))
                break

        logger.info('what is scan id?' + str(scanId))
        s = await db.getAttachment('scans', scanId, 'tiffsample.tif')
        checkpoint(s, 'Mock-reader uploads an attachment')

    async def createScanAndVerifyOutputs():
        await asyncio.sleep(2)
        async with ctx.dbDoc('readers', {"serialNumber": readerSerialNumber}) as r:

            nonlocal scan
            scan = await db.create('scans', scanBody)

            nonlocal scanId
            scanId = scan['_id']
            checkpoint(True, 'Created a scan '+scanId)

            analysisId = None
            analysis = None
            async def listenForAnalysisChanges():
                # again subscribe to everything because we don't know the id
                changes = db.getAllAndSubscribe('analyses')
                async for doc in changes:
                    if doc['_id'] != analysisId:
                        continue
                    if doc['status'] == 'RUNNING':
                        checkpoint(True, 'Analyzer updates analysis to "RUNNING"')
                    elif doc['status'] == 'COMPLETE':
                        checkpoint(True, 'Analyzer updates analysis to "COMPLETE"')
                        break
                    elif doc['status'] == 'ERROR':
                        checkpoint(False, 'Analyzer finished with errors:' + ','.join(doc['errors']))
                        break

                atts = await db.getAllAttachments('analyses', analysisId)
                checkpoint(len(atts) > 0, 'Analyzer uploads attachments')

            async def createAnalysis():
                await asyncio.sleep(5)
                analysisBody = {
                    "name": "My analysis!",
                    "protocol": "testProtocol1",
                    "protocolArgs": { "argument1": 0 },
                    "scanId": scanId
                }

                nonlocal analysis
                analysis = await db.create('analyses', analysisBody)

                nonlocal analysisId
                analysisId = analysis['_id']
                checkpoint(True, 'Created an analysis '+analysisId)


            await asyncio.gather(
                listenForAnalysisChanges(),
                createAnalysis()
            )
            await db.delete('analyses', analysisId)

         
        await asyncio.gather(
            listenForScanChanges(),
            createScanAndVerifyOutputs()
        )
        await db.delete('scans', scanId)

