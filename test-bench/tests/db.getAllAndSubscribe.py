import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 
import log
logger = log.getLogger('test-bench.tests.db.getAllAndSubscribe')

tags = ['db','scan']
requiredComponents = ['db', 'resource-api']

async def execute(checkpoint):
    
    # async with ctx.component('db'), ctx.component('resource-api'):

    scanBodies = [{ 
        "readerSerialNumber": "none",
        "name": "scan"+str(i),
        "productId": "test",
        "protocol": "pArray",
        "protocolArgs": {}
    } for i in range(1,10)]
    scanIds = []
    for s in scanBodies:
        scan = await db.create('scans', s)
        scanIds.append(scan['_id'])

    totalReceived = 0
    totalReceivedGoal = 2
    async def listen():
        nonlocal totalReceived 
        nonlocal totalReceivedGoal
        scan4s = db.getAllAndSubscribe('scans', {'name':'scan4', 'status':'QUEUED'})
        async for scan4 in scan4s:
            checkpoint(True,
                'Scans appear!: '+str(scan4))
            totalReceived += 1
            if totalReceived == totalReceivedGoal:
                break

    async def createNewScan4InASecond():
        await asyncio.sleep(2)
        scanx = await db.create('scans', {
            "readerSerialNumber": "none",
            "name":"scan4",
            "productId": "test",
            "protocol": "pArray",
            "protocolArgs": {}
        })
        scanIds.append(scanx['_id'])
    
    await asyncio.gather(
        listen(), 
        createNewScan4InASecond())

    for i in scanIds:
        await db.delete('scans', i)

