import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 
from datetime import datetime
import log
logger = log.getLogger('test-bench.tests.db.componentLifecycle')

requiredComponents = ['db', 'resource-api']

async def execute(checkpoint):

    componentClass = 'test-bench'
    compId = None

    async with ctx.dbDoc('components', {'class':componentClass}) as c:

        compId = c['_id']

        c = await db.get('components', c['_id'])
        checkpoint(c['class'] == componentClass,
            'Created component has the class supplied during creation')

        await db.update('components', {**c, 'newfield':4})
        c = await db.get('components', c['_id'])
        checkpoint(c['newfield'] == 4,
            'Components can be updated.')

        now = datetime.now().isoformat()
        await db.heartbeat('components', c['_id'])
        c = await db.get('components', c['_id'])
        checkpoint(c['lastHeartbeat'] > now,
            'Creating heartbeat writes timestamp onto component')

    async def getDoc():
        await db.get('components', compId)

    checkpoint(
        await utils.throwsAsync(getDoc),
        'Component document is deleted on context manager cleanup')

