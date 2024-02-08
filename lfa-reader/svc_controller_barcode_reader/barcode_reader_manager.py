import core.logging.log as log
import glob
import pyudev
import serial

logger = log.getLogger("controller_barcode_reader.bcreaderClient")

DEV_ID_VENDOR = "9901"
DEV_ID_MODEL = "0303"


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
        logger.info(f'Searching for barcode scanner on paths: {usbPaths}')
        for p in usbPaths:
            device = pyudev.Devices.from_device_file(udevCtx, p)
            vid = device.properties.get('ID_VENDOR_ID') 
            mid = device.properties.get('ID_MODEL_ID') 
            logger.info(f'Device at path {p} has vendorId "{vid}" and modelId "{mid}"')
            if vid == idVendor and mid == idModel:
                logger.info(f'Located barcode scanner at path "{p}"')
                self.devicePath = p
                break
            else:
                logger.error('Unable to locate barcode scanner.')

        assert self.devicePath
        self.device = serial.Serial(
            self.devicePath,
            self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
            timeout=self.timeout)

    def read(self) -> str:

        result = self.device.read_until(bytes(self.terminatingChar, self.encoding))
        result = result.decode(self.encoding)
        return result

    def readMostRecent(self) -> str:
        resultMostRecent = ""
        result = self.read()
        while result != "":
            resultMostRecent = result
            result = self.read()
        return resultMostRecent
