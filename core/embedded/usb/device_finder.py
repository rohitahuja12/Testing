import glob
import pyudev

def findUsbDevice(pattern):

    def patternMatches(dev, pat):
        return all([dev.properties.get(k) == v for k,v in pat.items()])

    udevCtx = pyudev.Context()
    usbPaths = glob.glob('/dev/ttyACM*')
    for p in usbPaths:
        device = pyudev.Devices.from_device_file(udevCtx, p)
        if patternMatches(device, pattern):
            return p

    return None

