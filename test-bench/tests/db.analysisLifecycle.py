import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 
import os
import log

logger = log.getLogger('test-bench.tests.db.analysisLifecycle')

tags = ['db','analysis']
requiredComponents = ['db', 'resource-api']

async def execute(checkpoint):

    analysisBody = { 
        "name": "My analysis!",
        "protocol": "pArray",
        "protocolArgs": {},
        "scanId": "scan123"
    }
    
    # async with ctx.component('db'), ctx.component('resource-api'):

    analysisId = None

    async with ctx.dbDoc('analyses', analysisBody) as a:

        analysisId = a['_id']
        checkpoint(a['status'] == 'QUEUED',
            'On creation, db assigns analysis status of "QUEUED"')

        await db.update('analyses', {**a, 'status': 'RUNNING'})
        a = await db.get('analyses', a['_id'])
        checkpoint(a['status'] == 'RUNNING',
            'Analysis status can be updated to "RUNNING"',
            a)

        await db.update('analyses', {**a, 'status': 'ERROR', 'errors': ["BOOM"]})
        a = await db.get('analyses', a['_id'])
        checkpoint(a['status'] == 'ERROR' and a['errors'][0] == "BOOM",
            'Analysis can be updated with "ERROR" status and an error message')

        with open('./images/tiffsample.tif', 'rb') as f:
            buf = f.read()
            await db.createAttachment('analyses', a['_id'], buf, 'attachment1.tif')

        allAttachments = await db.getAllAttachments('analyses', a['_id'])
        logger.info('all attachments respones: ' + str(a))
        att = next((a for a in allAttachments if a['filename'] == 'attachment1.tif'), None)
        checkpoint(att,
            'Analysis shows attachment metadata when attachment is created')
    
    async def getDoc():
        await db.get('analyses', analyisId)

    checkpoint(
        await utils.throwsAsync(getDoc),
        'Analysis document is deleted on context manager cleanup')

    checkpoint(
        await utils.throwsAsync(
            lambda: db.getAttachment('analyses', analysisId, 'attachment1.tif')),
        'Attachment gets deleted with analysis')
