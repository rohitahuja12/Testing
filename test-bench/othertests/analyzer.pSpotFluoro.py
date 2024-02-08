import os
import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 
import uuid
import shutil

tags = ['db','mock-reader']
requiredComponents = ['db','resource-api','analyzer']

async def execute(checkpoint):

    readerSerialNumber = "reader-"+str(uuid.uuid4())
    scanBody = { 
        "name": "My scan!",
        "readerSerialNumber": readerSerialNumber,
        "protocol": "pSpotFluoro",
        "protocolArgs": {},
        "volumeStorage": True,
        "productId": "kit1",
        "configIds": []
    }
    
    os.environ['MOCK_READER_ATTACHMENT_PATHS'] = '/testbenchstuff/images/pFluoro.tif'
    os.environ['MOCK_READER_ID'] = readerSerialNumber

    if not os.path.exists('/testbenchstuff/images'):
        os.makedirs('/testbenchstuff/images')

    if not os.path.exists('./testbenchstuff/images/pFluoro.tif'):
        shutil.copyfile(
            '/phoenix/images/pFluoro.tif', 
            '/testbenchstuff/images/pFluoro.tif')

    async with ctx.component('mock-reader'):

        async with ctx.dbDoc('readers', {"serialNumber": readerSerialNumber}) as r, ctx.dbDoc('scans', scanBody) as s:

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

