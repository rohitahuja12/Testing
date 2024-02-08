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

logger = log.getLogger('test-bench.tests.db.readerLifecycle')

tags = ['db','reader']
requiredComponents = ['db','resource-api']

async def execute(checkpoint):

    # async with ctx.component('db'), ctx.component('resource-api'):

    readerName = 'reader-'+str(uuid.uuid4())
    
    async with ctx.dbDoc('readers', {"serialNumber": readerName}) as r:

        r = await db.getAll('readers', {"serialNumber":readerName})
        reader = r[0]
        rid = reader['_id']
        checkpoint(rid,
            'Created reader exists and is retrievable by name')

        await db.update('readers', {**reader, 'newfield':4})
        logger.info('type of readerid: '+str(type(rid)))
        r2 = await db.get('readers', rid)
        checkpoint(r2['newfield'] == 4,
            'Readers can be updated.')

    checkpoint(True,
            "Reader Id value is: "+reader['_id'])
    checkpoint(reader['_id']==r2['_id'],
            "Ids between get and getAll are identical")

    async def getReader():
        await db.get('readers', rid)

    checkpoint(
        await utils.throwsAsync(getReader),
        'Reader document is deleted on context manager cleanup')

