import os
import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 
from datetime import datetime
import uuid
import log

logger = log.getLogger('test-bench.tests.db.defaultPlateMapLifecycle')

tags = []
requiredComponents = ['db', 'resource-api']

async def execute(checkpoint):

    # async with ctx.component('db'), ctx.component('resource-api'):

    dpmName = "defaultPlateMap1"
    dpmBody = {"name": dpmName}

    async with ctx.dbDoc('defaultPlateMaps', dpmBody) as m:

        m = await db.getAll('defaultPlateMaps', {"name":dpmName})
        dpm = m[0]
        dpmId = dpm['_id']
        checkpoint(dpmId,
            'Created default plate map exists and is retrievable by name')

        await db.update('defaultPlateMaps', {**dpm, 'newfield':4})
        dpm = await db.get('defaultPlateMaps', dpmId)
        checkpoint(dpm['newfield'] == 4,
            'Default plate maps can be updated.')

    async def getDefaultPlateMap():
        await db.get('defaultPlateMapts', dpmId)

    checkpoint(
        await utils.throwsAsync(getDefaultPlateMap),
        'Default Plate Map document is deleted on context manager cleanup')

