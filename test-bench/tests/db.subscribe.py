import threading
import asyncio
import sys
sys.path.insert(0, './common')
import dbclient as db
import contextManagers as ctx
import log
logger = log.getLogger('test-bench.tests.db.subscribe')

requiredComponents = ['db', 'resource-api']

async def execute(checkpoint):

    # async with ctx.component('db'), ctx.component('resource-api'):

    checkpoint(True, 'Started db and resource api')

    # Make a test component in a few seconds, once the listener is up
    async def makeTestComp():
        await asyncio.sleep(5)

        async with ctx.dbDoc('components', {'class':'test'}) as t:
            checkpoint(True, "Created a component called 'test'"+str(t))

    async def listen():
        async for change in db.subscribeToChanges():
            if change:
                checkpoint(True, "Can receive subscription message: "+str(change))
                break

    await asyncio.gather(
       listen(),
       makeTestComp())
        
