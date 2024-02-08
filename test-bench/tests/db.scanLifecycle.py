import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 

tags = ['db','scan']
requiredComponents = ['db', 'resource-api']

async def execute(checkpoint):

    scanBody = { 
        "name": "My scan!",
        "readerSerialNumber": "reader123",
        "protocol": "pArray",
        "productId": "kit1",
        "protocolArgs": {},
        "configIds": []
    }
    
    # async with ctx.component('db'), ctx.component('resource-api'):

    scanId = None

    async with ctx.dbDoc('scans', scanBody) as s:

        scanId = s['_id']
        checkpoint(s['status'] == 'QUEUED',
            'On creation, db assigns scan status of "QUEUED"')

        await db.update('scans', {**s, 'status': 'RUNNING'})
        s = await db.get('scans', s['_id'])
        checkpoint(s['status'] == 'RUNNING',
            'Scan status can be updated to "RUNNING"')

        await db.update('scans', {**s, 'status': 'ERROR', 'errors': ["BOOM"]})
        s = await db.get('scans', s['_id'])
        checkpoint(s['status'] == 'ERROR' and s['errors'][0] == "BOOM",
            'Scan can be updated with error status and an error message')

        with open('./images/tiffsample.tif', 'rb') as f:
            buf = f.read()
            await db.createAttachment('scans', s['_id'], buf, 'attachment1.tif')

        s = await db.getAttachment('scans', s['_id'], 'attachment1.tif')
        checkpoint(s, 'Scan shows attachment metadata when attachment is created')

    
    async def getDoc():
        await db.get('scans', scanId)

    checkpoint(
        await utils.throwsAsync(getDoc),
        'Document is deleted on context manager cleanup')
