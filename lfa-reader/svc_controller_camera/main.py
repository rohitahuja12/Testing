import sys
sys.path.insert(0, '.')
import core.logging.log as log
import os
import multiprocessing as mp
from camera_manager import CameraManager
from core.codec.artifact_codec import ArtifactCodec
from core.embedded.hardware_controller.synchronous_request.server import HardwareRequestServer
from core.embedded.hardware_controller.synchronous_request.command_table import CommandTable
from core.embedded.hardware_controller.streaming.server import spawnBinaryEventStream

logger = log.getLogger("controller_camera.main")
codec = ArtifactCodec()

requestTransport = os.environ['CONTROLLER_CAMERA_REQUEST_TRANSPORT']
imageStreamTransport = os.environ['CONTROLLER_CAMERA_IMAGE_STREAM_TRANSPORT']


def main():

    # initialize camera
    imageQueue = mp.JoinableQueue(10)
    camera = CameraManager(imageQueue)

    spawnBinaryEventStream(
        imageStreamTransport,
        imageQueue,
        encode=lambda i: codec.arrayToTiff(i[1], prefix=i[0]))

    # # main application loop
    HardwareRequestServer( 
        requestTransport, 
        CommandTable.fromObject(camera))


if __name__ == '__main__':
    main()

