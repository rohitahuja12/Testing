import sys
sys.path.insert(0, '.')
import core.logging.log as log
import os
#from datetime import datetime as dt

from core.embedded.hardware_controller.synchronous_request.server import HardwareRequestServer
from core.embedded.hardware_controller.synchronous_request.command_table import CommandTable

from barcode_reader_manager import BarcodeReaderManager

logger = log.getLogger("controller_barcodereader_reader.main")

requestTransport = os.environ['CONTROLLER_BARCODEREADER_REQUEST_TRANSPORT']

def main():

    bcreaderManager = BarcodeReaderManager()

    HardwareRequestServer( 
        requestTransport, 
        CommandTable.fromObject(bcreaderManager))


if __name__ == '__main__':
    main()
