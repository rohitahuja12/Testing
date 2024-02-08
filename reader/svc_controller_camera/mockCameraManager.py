import sys
sys.path.insert(0, './common')
import eventLogging
import log

logger = log.getLogger("svc_controller_camera.mockControllerCamera")
event = eventLogging.get_event_logger(logger)

class CameraManager():
    handle = None
    eightBit = False
    session = None
    sensorMicronsPerPixelX = None
    sensorMicronsPerPixelY = None
    mirrorX = None
    mirrorY = None
    rotation = None
    clientLock = None

    def __init__(self, imageQueues, boardTransport):
        logger.info("Mock CameraManager.__init__")
        logger.info("imageQueues: ", imageQueues)
        logger.info("boardTransport: ", boardTransport)

    def connect(self):
        logger.info("Mock CameraManager.connect")
        return True
    
    def exposeSync(self, millis: int) -> str:
        logger.info("Mock CameraManager.exposeSync")
        return b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='