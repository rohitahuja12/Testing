import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
sys.path.insert(0, '.')
import apiClient
import asyncio
import base64
import eventLogging
import io
import json
import lib_db_reader_status.client as readerStatusDb
import lib_db_task_results.client as taskResultsDb
import lib_hardware_interface.client as hwclient
import log
import os
import time
import traceback
from reader.utils.apiAuthProvider import APIAuthProvider
from taskStatusHandler import taskStatusHandler
from zipfile import ZipFile
from readerCacheHelper import getEncodedCachedValueOrRunFetch

api = apiClient.APIClient(APIAuthProvider())
logger = log.getLogger("reader_task_worker.processor")
event = eventLogging.get_event_logger(logger)

ownpid = os.getpid()
logger.info(f'OWNPID: {ownpid}')

barcodeReaderRequestTransport = os.environ['CONTROLLER_BARCODEREADER_REQUEST_TRANSPORT']
cameraRequestTransport = os.environ['CONTROLLER_CAMERA_REQUEST_TRANSPORT']
stageRequestTransport = os.environ['CONTROLLER_STAGE_REQUEST_TRANSPORT']
boardRequestTransport = os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']
locationsRequestTransport = os.environ['LOCATIONS_REQUEST_TRANSPORT']
cacheRequestTransport = os.environ['READER_CACHE_REQUEST_TRANSPORT']
rtw_state_listener_transport = os.environ['TASK_WORKER_TASK_STATE_LISTENER_TRANSPORT']


async def getReader(readerSerial):

    async def _fetch():
        readers = await api.getAll('readers', {'serialNumber':readerSerial})
        if not readers:
            raise Exception(f"Failed to retrieve reader configuration with serial {readerSerial}")
        reader = readers[0]
        return reader

    reader = await getEncodedCachedValueOrRunFetch(
        key = 'reader',
        fetch = _fetch)

    return reader

async def getReaderSerial(boardTransport):

    async def _fetch():

        board = hwclient.HardwareClient(boardTransport)
        while True:
            try:
                readerSerial = board.getSerialNumber()
                break
            except Exception as e:
                logger.warn(f'Error connecting to board, retrying. {e}')
                time.sleep(1)
        return readerSerial

    readerSerial = await getEncodedCachedValueOrRunFetch(
        key = 'readerSerial',
        fetch = _fetch)

    return readerSerial


async def main(protocols, taskId=None, protocolName=None, protocolArgs={}):

    try:
        event(f'EVENT_RTW_STARTED_TASK taskId={taskId} protocolName={protocolName}')

        task = None
        if taskId:
            task = await api.get('scans', taskId)
            # maybe do some checks here to make sure we're ready to go?

            logger.info('Running a task with id '+taskId)
            # load protocol
            protocol = protocols[task['protocol']]
        else:
            logger.info('Running an anonymous task with name '+protocolName)
            protocol = protocols[protocolName]

        async def process():

            async def getTaskArtifact(taskId, name):
                return await api.getAttachment('scans', taskId, name)

            async def createTaskArtifactZip(results, tId=taskId):
                '''
                Takes a dict[str, bin],
                creates a zip file and queues it for uploading
                '''
                output = io.BytesIO()
                with ZipFile(output, mode='w') as zipf:
                    for name, value in results.items():
                        zipf.writestr(name, value)
                output = output.getvalue()
                taskResultsDb.queueResult(tId, output)

            async def getProduct(productId):
                return await api.get('products', productId)

            async def invokeProtocol(taskId=None, protocolName=None, protocolArgs=None):
                return await main(protocols, taskId, protocolName, protocolArgs)

            # initialize the reader hardware
            serial = await getReaderSerial(boardRequestTransport)
            reader = await getReader(serial)
            barcode_reader = hwclient.HardwareClient(barcodeReaderRequestTransport)
            camera = hwclient.HardwareClient(cameraRequestTransport)
            board = hwclient.HardwareClient(boardRequestTransport)
            stage = hwclient.HardwareClient(stageRequestTransport)
            locations = hwclient.HardwareClient(locationsRequestTransport)
            cache = hwclient.HardwareClient(cacheRequestTransport)

            if task:
                args = task.get('protocolArgs', None)
            else:
                args = protocolArgs

            context = {

                # data
                'task': task,
                'reader': reader,
                'protocols': protocols,
                'args': args,

                # services
                'barcodeReader': barcode_reader,
                'camera': camera,
                'board': board,
                'stage': stage,
                'locations': locations,
                'cache': cache,

                # callbacks
                'getTaskArtifact': getTaskArtifact,
                'getProduct': getProduct,
                'createArtifact': createTaskArtifactZip,
                'invokeProtocol': invokeProtocol
            }

            board.setIsAuxPowerOn(True)

            results = await protocol['module'].execute(context)
            if task:
                task['results'] = results
                await api.update('scans', task)

            board.setIsAuxPowerOn(False)

        if taskId:
            result = await taskStatusHandler(task, process)
        else:
            result = await process()
        
        event('EVENT_RTW_COMPLETED_TASK')

    except Exception as e:
        msg = f'This is bad: {e} {traceback.format_exc()}'
        logger.error(msg)
        event('EVENT_RTW_FAILED_TASK')
        raise


if __name__ == '__main__':
    asyncio.run(main())



