import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import asyncio
import log
import lib_hardware_interface.client as hwclient
import apiClient
import os
import time
import json
from utils.apiAuthProvider import APIAuthProvider
from locationManager import LocationManager
from readerCacheHelper import getEncodedCachedValueOrRunFetch

api = apiClient.APIClient(APIAuthProvider())
logger = log.getLogger("svc_locations.main")

requestTransport = os.environ['LOCATIONS_REQUEST_TRANSPORT']
boardTransport = os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']

def generateCommandTable(locationManager):
    table = {
        "help": lambda: table,
        # make all methods of locationManager callable through this interface
        **{
            name:getattr(locationManager, name)
            for name in dir(locationManager) 
            if callable(getattr(locationManager, name))
            and not name.startswith('__')
        }
    }
    return table

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

def getReaderSerial(boardTransport):

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

    readerSerial = asyncio.run(getEncodedCachedValueOrRunFetch(
        key = 'readerSerial',
        fetch = _fetch))

    return readerSerial

def main():

    logger.info('hi, im locations')

    serial = getReaderSerial(boardTransport)
    reader = getReader(serial)
    locationManager = LocationManager(reader)

    hwclient.HardwareRequestServer(
        requestTransport,
        generateCommandTable(locationManager))

if __name__ == '__main__':
    main()
