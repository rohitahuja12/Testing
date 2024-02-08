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

logger = log.getLogger('test-bench.tests.db.productLifecycle')

tags = ['db','reader']
requiredComponents = ['db', 'resource-api']


async def execute(checkpoint):

    # async with ctx.component('db'), ctx.component('resource-api'):

    productId = "product1"
    productBody = {
        "productId": productId,
        "units": "microns",
        "exposures": [],
        "recommendedDilutionFactor": 0,
        "recommendedInitialConcentration": 0,
        "features": []
    }

    async with ctx.dbDoc('products', productBody) as p:

        p = await db.getAll('products', {"productId":productId})
        product = p[0]
        pid = product['_id']
        checkpoint(pid,
            'Created product exists and is retrievable by name')

        await db.update('products', {**product, 'newfield':4})
        p = await db.get('products', pid)
        checkpoint(p['newfield'] == 4,
            'Products can be updated.')

    async def getProduct():
        await db.get('products', pid)

    checkpoint(
        await utils.throwsAsync(getProduct),
        'Product document is deleted on context manager cleanup')

