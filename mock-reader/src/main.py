import sys
sys.path.insert(0, './common')
import dbclient as db
import artifactCodec
import heartbeat
import timing
import time
import utils
import multiprocessing as mp
import log
import json
import os
import asyncio

compClass = 'mock-reader'
logger = log.getLogger('mock-reader.src.main')
attachments = os.environ['MOCK_READER_ATTACHMENT_PATHS'].split(',')
readerId = os.environ['MOCK_READER_ID']

logger.info('Running mock reader with readerId '+readerId+
    ' and attachment paths: '+ str(attachments))

state = {
    "lidState": None, # OPEN, CLOSED
    "connectState": None, # CONNECTED, DISCONNECTED
    "errorMessage": None, # message string 
}

if __name__ == "__main__":
    try:

        # # register self (container) with db
        # # heartbeat periodically
        # # if connection to db ends, entire process will shutdown...probably not what we want long-term
        # the process should gracefully abandon the current scan and wait for the db to come back up
        compId = None
        retryPause = 10
        while compId == None:

            try:
                compId = asyncio.run(heartbeat.registerAndStartComponentHeartbeat(compClass))
                logger.info('Registered self with component id: '+compId['_id'])

            except Exception as e:
                logger.info('Error connecting to database, retrying in '+str(retryPause)+' seconds: ' + str(e))
                time.sleep(retryPause)

        
        async def processScan(scan):

            try:
                logger.info('found scan '+ json.dumps(scan))

                scan = await db.update('scans', {**scan, 'status':'RUNNING'})
                
                logger.info('updated scan '+ json.dumps(scan))
                scan = await db.get('scans', scan['_id'])
                logger.info('retreived-after-update scan '+ json.dumps(scan))
                # wait a bit and then update scan to 'COMPLETE' and attach some fake images
                ls = os.listdir('/testbenchstuff')
                logger.info('list /testbenchstuff: '+str(ls))
                for attachmentPath in attachments:
                    name = os.path.basename(attachmentPath)
                    with open(attachmentPath, 'rb') as f:
                        logger.info('attempting to attach file '+attachmentPath+' to scan '+scan['_id'])
                        
                        result = await db.createAttachment('scans', scan['_id'], f.read(), name)
                        logger.info('Attachment complete.')

                scan = await db.update('scans', {**scan, 'status':'COMPLETE'})
                logger.info('completed scan')
            except Exception as e:
                logger.error(e)
                await db.update('scans', {**scan, 'status':'ERROR', 'errors':[*scan['errors'], str(e)]})
                
        async def processContinuously():
            scans = db.getAllAndSubscribe('scans',{'status':'QUEUED'})
            async for scan in scans:
                logger.info('scan: '+str(scan))
                await processScan(scan)

        asyncio.run(processContinuously())

    except Exception:
        logger.exception('blew up')

