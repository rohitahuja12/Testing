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

logger = log.getLogger('test-bench.tests.db.configLifecycle')

tags = []
requiredComponents = ['db', 'resource-api']

async def execute(checkpoint):

    # async with ctx.component('db'), ctx.component('resource-api'):

    configName = "myconfig"
    configEntity = "someentity"
    configBody = {
        "name": configName, 
        "entityId": configEntity,
        "value": {"x":4}
    }

    async with ctx.dbDoc('configs', configBody) as m:

        m = await db.getAll(
            'configs', 
            {"name":configName, "entityId": configEntity})

        config = m[0]
        configId = config['_id']
        checkpoint(configId,
            'Created config exists and is retrievable by name+entityId')

        await db.update('configs', {**config, 'value':{'x':5}})
        config = await db.get('configs', configId)
        checkpoint(config['value']['x'] == 5,
            'Configs can be updated.')

    async def getConfigs():
        await db.get('configs', configId)

    checkpoint(
        await utils.throwsAsync(getConfigs),
        'Config document is deleted on context manager cleanup')

