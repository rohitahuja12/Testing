import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 

tags = ['db','scan']
requiredComponents = ['db', 'resource-api']

async def execute(checkpoint):
    
    scan4s = await db.getAll('scans', {'name':'scan4'})
    for scan in scan4s:
        await db.delete('scans', scan['_id'])

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

    scan4s = await db.getAll('scans', {'name':'scan4'})
    checkpoint(len(scan4s)==1 and scan4s[0]['name']=='scan4', 
        'Can retrieve items with a filter by name.')

    sid = scan4s[0]['_id']
    scan4s = await db.getAll('scans', {'_id':sid})
    checkpoint(True,
        "scan 4s: "+str(scan4s))
    checkpoint(len(scan4s)==1 and scan4s[0]['_id']==sid, 
        'Can retrieve items with a filter by _id.')
    

    for i in scanIds:
        await db.delete('scans', i)

