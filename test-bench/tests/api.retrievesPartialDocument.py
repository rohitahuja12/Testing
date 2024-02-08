import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 
import os
import log

logger = log.getLogger('test-bench.tests.api.retrievesPartialDocument')

requiredComponents = ['db', 'resource-api']

async def execute(checkpoint):

    analysisBody = { 
        "name": "My analysis!",
        "protocol": "pArray",
        "protocolArgs": {},
        "scanId": "scan123"
    }
    
    # async with ctx.component('db'), ctx.component('resource-api'):


    async with ctx.dbDoc('analyses', analysisBody) as a:

        analyses = await db.getAll('analyses', {'omit': 'protocolArgs'})
        res = next(x for x in analyses if x['_id'] == a['_id'])
        checkpoint(
            not res.get('protocolArgs', None),
           "Omit field removes that field from results")

