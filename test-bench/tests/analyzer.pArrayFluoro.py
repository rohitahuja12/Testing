import os
import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 
import uuid
import shutil
import log
import json
import imageio

import dataGenerators.scanImageGenerator as imgGen

requiredComponents = ['db','resource-api','analyzer']

logger = log.getLogger('test-bench.tests.analyzer.pArray.Fluoro')
analysisBody = None

async def execute(checkpoint):

    readerSerialNumber = "reader-"+str(uuid.uuid4())
    with open("/phoenix/test-data/products/r12plex_020822_4400.json") as f:
        productBody = json.load(f)

    scanBody = lambda productId: { 
        "name": "Array Scan 1",
        "productId": productId,
        "readerSerialNumber": readerSerialNumber,
        "protocol": "pArrayFluoro",
        "protocolArgs": {
            "images": [
                # images of every well in the plate.
                {
                    "region": [
                        {
                            "feature": [
                                "Well",
                                column,
                                row
                            ]
                        }
                    ]
                }
                for column in ["A","B","E","F"]
                for row in range(1,13)
            ]
        },
        "status":"COMPLETE"
    }

    async with ctx.dbDoc('readers', {"serialNumber": readerSerialNumber}) as r, ctx.dbDoc('products', productBody) as p:
        
        productId = p['_id']
        async with ctx.dbDoc('scans', scanBody(productId)) as s:
            checkpoint(True, 'Created a product '+p['_id'])
            checkpoint(True, 'Created a scan '+s['_id'])
            for column in ["A","B","E","F"]:
                for row in range(1,13):
                    with open(f'/phoenix/images/pArrayWholePlateScan/{column}{row}',"rb") as f:
                        await db.createAttachment(
                            "scans",
                            s['_id'],
                            f.read(),
                            f'{column}{row}')
            atts = await db.getAllAttachments('scans', s['_id'])
            checkpoint(True, 'Created attachments for rows A and B '+str(atts))

            global analysisBody
            analysisBody['scanId'] = s['_id']
            logger.info("Inline analysis body: "+str(analysisBody))

            # async with ctx.dbDoc('analyses', analysisBody) as a:
            a = await db.create('analyses', analysisBody)

            checkpoint(True, 'Created an analysis '+a['_id'])

            changes = db.getAllAndSubscribe('analyses')
            async for doc in changes:
                if doc['_id'] != a['_id']:
                    continue
                elif doc['status'] == 'COMPLETE':
                    checkpoint(True, 'Analyzer updates analysis to "COMPLETE"')
                    break
                elif doc['status'] == 'ERROR':
                    checkpoint(False, 'Analyzer finished with errors:' + ','.join(doc['errors']))
                    break

            attachments=await db.getAllAttachments("analyses",a['_id'])
            logger.info(str(attachments) )
            for attachment in attachments:
                fileName = attachment["filename"]
                attFb =  await db.getAttachment("analyses",a['_id'],fileName)
                with open(str("/phoenix/test-data-output/"+fileName),"wb") as f:
                    f.write(attFb)

            #successfully generates test images
            #resultImage = imgGen.createArrayTestImage(341,341)
            #logger.info("Test image created"+str(type(resultImage)))
            #imageio.mimwrite("/phoenix/test-data-output/stack-513.tif",resultImage)

#analysis doc for test #2 - has 2 unknowns
dilutionFactor = 3
analysisBody = {
    "name": "pSpotFluoro.run2",
    "scanId": None,
    "protocol": "pArrayFluoro",
    "protocolArgs": {
        "standardDilutionFactor": dilutionFactor,
        "initialConcentrations": {
            "IL-1a": 200,
            "IL-1B": 2000,
            "IL-2": 600,
            "IL-4": 30,
            "IL-5": 600,
            "IL-6": 200,
            "IL-8": 600,
            "IL-10": 600,
            "IL-13": 600,
            "IFG-y": 2000,
            "MCP-1": 2000,
            "TNF-a": 2000
        },
        "initialConcentrationUnits": "pg/ml",
        "wells": [
            # standards
            *[
                {
                    "label": f"stnd{column}",
                    "row": row,
                    "column": str(column),
                    "type": "standard",
                    "replicateIndex": 1 if row == "A" else 2
                }
                for column in range(1,12)
                for row in ["A","B"]
            ],
            # blanks
            {
                "label": f"blank",
                "row": "A",
                "column": "12",
                "type": "blank",
                "replicateIndex": 1
            },
            {
                "label": f"blank",
                "row": "B",
                "column": "12",
                "type": "blank",
                "replicateIndex": 2
            },
            # unknows
            *[
                {
                    "label": f"unknown{str(column).zfill(2)}",
                    "row": row,
                    "column": str(column),
                    "type": "unknown",
                    "replicateIndex": 1 if row == "E" else 2
                }
                for column in range(1,13)
                for row in ["E","F"]
            ]
        ]
    }
}
