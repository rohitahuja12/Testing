import sys
sys.path.insert(0, '.')
import reader.lib_hardware_interface.client as c

# host = '192.168.1.23'
host='localhost'
cam = c.HardwareClient(f'tcp://{host}:8110')
stage = c.HardwareClient(f'tcp://{host}:8100')
stagekiller = c.HardwareClient(f'tcp://{host}:8104')
board = c.HardwareClient(f'tcp://{host}:8120')
locations = c.HardwareClient(f'tcp://{host}:8130')

# locations.setProduct('643589c118f4608414de3e44')

def moveToFeature(name, offx=0, offy=0):
    f = locations.getPoint(name)
    cc = locations.getPoint("cameraCenter")
    stage.setPosUm(cc['x']-f['x']+offx, cc['y']-f['y']+offy)
