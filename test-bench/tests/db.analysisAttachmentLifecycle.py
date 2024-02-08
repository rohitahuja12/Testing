import sys
sys.path.insert(0, './common')
import dbclient as db
import artifactCodec 
import asyncio
import contextManagers as ctx
import utils 
import os
import log
import shutil

logger = log.getLogger('test-bench.tests.db.analysisAttachmentLifecycle')
codec = artifactCodec.ArtifactCodec()

tags = ['db','analysis']
requiredComponents = ['db', 'resource-api']

async def execute(checkpoint):

    analysisBody = { 
        "name": "My analysis!",
        "protocol": "pArray",
        "protocolArgs": {},
        "scanId": "scan123"
    }

    if not os.path.exists('/testbenchstuff/images'):
        os.makedirs('/testbenchstuff/images')

    if not os.path.exists('./testbenchstuff/images/pFluoro.tif'):
        shutil.copyfile(
            '/phoenix/images/pFluoro.tif', 
            '/testbenchstuff/images/pFluoro.tif')
    
    # async with ctx.component('db'), ctx.component('resource-api'):

    analysisId = None

    async with ctx.dbDoc('analyses', analysisBody) as a:

        analysisId = a['_id']

        orig = open('/testbenchstuff/images/pFluoro.tif', 'rb').read()
        await db.createAttachment(
            'analyses', 
            analysisId,
            orig,
            "randoAttach.tif")

        res = await db.getAttachment('analyses', analysisId, "randoAttach.tif")
        
        checkpoint(hash(orig) == hash(res),
            "Storing and retrieving attachments does not alter their content")

        await db.deleteAttachment('analyses', analysisId, "randoAttach.tif")

        async def getIt():
            await db.getAttachment('analyses', analysisId, "randoAttach.tif")

        checkpoint(await utils.throwsAsync(getIt),
            "Analysis attachment is deleted after test")

