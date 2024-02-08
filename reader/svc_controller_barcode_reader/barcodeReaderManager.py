import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
from lib_hardware_interface.client import InternalError
import log
import glob
import pyudev
import serial
import time
logger = log.getLogger("controller_barcode_reader.boardClient")

DEV_ID_VENDOR = "0483"
DEV_ID_MODEL = "5740"


class BarcodeReaderManager():

    def __init__(self, idVendor=DEV_ID_VENDOR, idModel=DEV_ID_MODEL):

        self.baudrate = 9600
        self.timeout = 1
        self.bytesize=serial.EIGHTBITS
        self.parity=serial.PARITY_NONE
        self.stopbits=serial.STOPBITS_TWO
        self.terminatingChar = '\r'
        self.encoding = 'ascii'

        udevCtx = pyudev.Context()
        usbPaths = glob.glob('/dev/ttyACM*')
        logger.info(f'Searching for board on paths: {usbPaths}')
        for p in usbPaths:
            device = pyudev.Devices.from_device_file(udevCtx, p)
            vid = device.properties.get('ID_VENDOR_ID') 
            mid = device.properties.get('ID_MODEL_ID') 
            logger.info(f'Device at path {p} has vendorId "{vid}" and modelId "{mid}"')
            if vid == idVendor and mid == idModel:
                logger.info(f'Located board at path "{p}"')
                self.devicePath = p
                break
            else:
                logger.error('Unable to locate board.')

        assert self.devicePath
        self.device = serial.Serial(
            self.devicePath,
            self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
            timeout=self.timeout)

    def read(self) -> str:
        readcmd = b'\x02\x01\x01\x02\xef\x03\x00\x00\x00\x00\x00\x00\x00\x00\x03\x05'
        self.device.write(readcmd)
        result = self.device.read_until(bytes(self.terminatingChar, self.encoding))
        result = result.replace(b'\r', b'')
        result = result.decode(self.encoding)
        logger.info(f'Barcode reader read value {result}')
        return result
