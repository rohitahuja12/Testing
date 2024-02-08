import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 
import log
logger = log.getLogger('test-bench.tests.db.getAllAndSubscribe2')

tags = ['db','scan']
requiredComponents = ['db', 'resource-api']

async def execute(checkpoint):
    
    # async with ctx.component('db'), ctx.component('resource-api'):

    def buildScan(name):
        return { 
            "readerSerialNumber": "none",
            "name": "scan"+str(name),
            "productId": "test",
            "protocol": "pArray",
            "protocolArgs": {}
        }
    scans = [buildScan(i) for i in range(1,10)]
    checkpoint(True, str(scans))
    scans = await asyncio.gather(*[db.create('scans', s) for s in scans])

    totalReceived = 0
    totalReceivedGoal = 2
    async def listen():
        nonlocal totalReceived 
        nonlocal totalReceivedGoal
        scan4s = db.getAllAndSubscribe('scans', {'status':'QUEUED'})
        scan5s = db.getAllAndSubscribe('scans', {'_id':'62d982c778f6ef2803eec857'})
        async for s in scan5s:
            print('mmmm')
        async for scan4 in scan4s:
            logger.info(scan4)
            checkpoint(scan4['status'] == 'QUEUED',
                'Scans with same status appear!: '+str(scan4))
            totalReceived += 1
            if totalReceived == totalReceivedGoal:
                break

    async def updateScanToComplete():
        await asyncio.sleep(2)
        scanx = await db.update('scans', {**scans[0], "status":"COMPLETE"})
        checkpoint(True, "Set scan status to COMPLETE, should not show up on event stream")
        await asyncio.sleep(2)
        scanx = await db.update('scans', {**scans[0], "status":"QUEUED"})
        checkpoint(True, "Set scan status to QUEUED, should show up on event stream and terminate test")
    
    await asyncio.gather(
        listen(), 
        updateScanToComplete())

    for s in scans:
        await db.delete('scans', s['_id'])

