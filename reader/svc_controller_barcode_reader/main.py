import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import asyncio
import lib_hardware_interface.client as hwclient
import log
import multiprocessing as mp
import os
import time
import json
from datetime import datetime as dt
logger = log.getLogger("controller_barcodereader.main")

from barcodeReaderManager import BarcodeReaderManager

requestTransport = os.environ['CONTROLLER_BARCODEREADER_REQUEST_TRANSPORT']

def generateCommandTable(obj):
    table = {
        "help": lambda: table,
        # make all methods of bcreader client callable through this interface
        **{
            name:getattr(obj, name)
            for name in dir(obj) 
            if callable(getattr(obj, name))
            and not name.startswith('__')
        },
    }
    return table

def main():

    bcreaderManager = BarcodeReaderManager()

    hwclient.HardwareRequestServer(
        requestTransport,
        generateCommandTable(bcreaderManager))


if __name__ == '__main__':
    main()
