import json
import sys
sys.path.insert(0, "./common")
import dbclient
import asyncio
import os
import cv2
import dbclient as db
from artifactCodec import ArtifactCodec
codec = ArtifactCodec()

async def handle (args):

    readerSerial = args["<readerSerialNumber>"]

    scanBody = {
      "name": "live scan from PHX CLI",
      "productId": "",
      "protocol": "live",
      "protocolArgs": {
          # NONE -> no command have been issued yet
          # PENDING -> a command has been issued
          # PROCESSING -> the reader is processing the last command 
          # COMPLETE -> the reader has completed processing the last command
          "stepStatus": "NONE",
          "collectImage": True,
          "exposure": 3000,
          "laserOn": True,
      },
      "readerSerialNumber": readerSerial
    }

    scan = await db.create('scans', scanBody)

    await runRepl(scan)

async def runRepl(scan):

    print(f"Live scan started: {scan['_id']}")
    print(json.dumps(scan['protocolArgs'], indent=4))
    try:
        while True:

            args = scan['protocolArgs']

            # get user input (partial scan)
            cmd = input('>')
            try:
                cmd = json.loads(cmd)
            except Exception:
                print('invalid json')
                continue

            # update scan
            args = {**args, **cmd, 'stepStatus': 'PENDING'}
            scan = {**scan, 'protocolArgs':args}
            scan = await db.update('scans', scan)

            # poll scan for stepStatus to change to 'PROCESSING'
            states = watchStepStatus(scan)
            async for state, scan in watchStepStatus(scan):
                if state == 'PROCESSING':
                    print('Reader is PROCESSING')
                    continue
                if state in ['COMPLETE','ERROR']:
                    args = scan['protocolArgs']
                    print(json.dumps(args, indent=4))
                    if args['collectImage']:
                        await displayLastFrame(scan['_id'])
                    break
                else:
                    print(f'Reader reached unknown state {state}')
    finally:
        scan = {**scan, 'status': 'COMPLETE'}
        await db.update('scans', scan)

    
async def watchStepStatus(scan):
    oldStepStatus = scan['protocolArgs']['stepStatus']
    while True:
        await asyncio.sleep(0.25)
        newScan = await db.get('scans', scan['_id'])
        newStepStatus = newScan['protocolArgs']['stepStatus']
        if newStepStatus == oldStepStatus:
            continue
        oldStepStatus = newStepStatus
        yield oldStepStatus, newScan

async def displayLastFrame(scanId):
    frame = await db.getAttachment('scans', scanId, 'frame')
    im = codec.tiffToArray(frame)
    cv2.imshow("frame", im)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
