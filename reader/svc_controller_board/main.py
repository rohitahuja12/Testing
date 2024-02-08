import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import asyncio
import apiClient
import lib_hardware_interface.client as hwclient
import log
import multiprocessing as mp
import os
import time
import json
from datetime import datetime as dt
from readerCacheHelper import getEncodedCachedValueOrRunFetch
from utils.apiAuthProvider import APIAuthProvider

logger = log.getLogger("controller_board.main")
api = apiClient.APIClient(APIAuthProvider())

mock = os.environ.get('CONTRO LLER_BOARD_MOCK', 'false').lower() == 'true'

if mock:
    from mockBoardClient import BoardClient, BoardError
else:
    from boardClient import BoardClient, BoardError

requestTransport = os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']
streamTransport = os.environ['CONTROLLER_BOARD_STREAM_TRANSPORT']
errorStreamTransport = os.environ['CONTROLLER_BOARD_ERROR_STREAM_TRANSPORT']
boardTransport = os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']

def generateCommandTable(boardClient):
    table = {
        "help": lambda: table,
        # make all methods of board client callable through this interface
        **{
            name:getattr(boardClient, name)
            for name in dir(boardClient) 
            if callable(getattr(boardClient, name))
            and not name.startswith('__')
        },
    }
    return table

def startButtonPressStream(queue):
    status = {}
    client = hwclient.HardwareClient(requestTransport)
    while True:

        pressed = client.getButtonPressed()
        if pressed:
            status = { "buttonPressed": pressed }
            queue.put({**status, "timestamp": dt.now().isoformat()})

            count = 1 
            while client.getButtonPressed():
                if count%10 == 0:
                    logger.info(f'Reset button {count} times.')
                client.clearButtonPressed()

        time.sleep(0)

def startErrorStream(queue):
    client = hwclient.HardwareClient(requestTransport)
    logger.info('************RUNNING ERROR STREAM')

    lastError = None
    while True:

        error = client.getEmergencyValue()
        if error != lastError:
            lastError = error
            msg = { "code": error, "name": BoardError(error).name }
            queue.put({**msg, "timestamp": dt.now().isoformat()})

        time.sleep(0)

def getReader(readerSerial):

    async def _fetch():
        readers = await api.getAll('readers', {'serialNumber':readerSerial})
        if not readers:
            raise Exception(f"Failed to retrieve reader configuration with serial {readerSerial}")
        reader = readers[0]
        return reader

    reader = asyncio.run(getEncodedCachedValueOrRunFetch(
        key = 'reader',
        fetch = _fetch))

    return reader


def main():

    streamQueue = mp.JoinableQueue()
    p1 = mp.Process(target=startButtonPressStream, args=(streamQueue,))
    p1.start()
    logger.info('started stream proc')

    errorStreamQueue = mp.JoinableQueue()
    p2 = mp.Process(target=startErrorStream, args=(errorStreamQueue,))
    p2.start()
    logger.info('started error stream proc')

    board = BoardClient()
    reader = getReader(board.getSerialNumber())

    logger.info(f'type of reader: {type(reader)}')
    logger.info(f'reader: {reader}')

    board.setMicronsPerStepZ(reader['micronsPerMotorStepZ'])
    board.setMotorZLimitSteps(reader['stageLimitStepsZ'])
    logger.info('started board client')

    hwclient.spawnJsonEventStream(
        streamTransport,
        streamQueue)
    logger.info('started event stream zmq')
    
    hwclient.spawnJsonEventStream(
        errorStreamTransport,
        errorStreamQueue)
    logger.info('started error stream zmq')

    hwclient.HardwareRequestServer(
        requestTransport,
        generateCommandTable(board))


if __name__ == '__main__':
    main()
