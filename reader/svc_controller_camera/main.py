import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import base64
import cv2
import inspect
import io
import itertools
import json
import lib_hardware_interface.client as hwclient
import log
import multiprocessing as mp
import numpy as np
import os
import threading
import time
import types
from artifactCodec import ArtifactCodec
from datetime import datetime as dt
from enum import Enum
from queue import Empty
logger = log.getLogger("controller_camera.main")
codec = ArtifactCodec()

mock = os.environ.get('CONTROLLER_CAMERA_MOCK', 'false').lower() == 'true'

if mock:
    from mockCameraManager import CameraManager
else:
    from cameraManager import CameraManager


requestTransport = os.environ['CONTROLLER_CAMERA_REQUEST_TRANSPORT']
streamTransport = os.environ['CONTROLLER_CAMERA_STREAM_TRANSPORT']
imageStreamTransport = os.environ['CONTROLLER_CAMERA_IMAGE_STREAM_TRANSPORT']
compressedImageStreamTransport = os.environ['CONTROLLER_CAMERA_COMPRESSED_IMAGE_STREAM_TRANSPORT']

boardTransport = os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']



def generateCommandTable(cameraManager):
    table = {
        "help": lambda: table,
        # make all methods of camera manager callable through this interface
        **{
            name:getattr(cameraManager, name)
            for name in dir(cameraManager) 
            if callable(getattr(cameraManager, name))
            and not name.startswith('__')
        },

    }
    return table


    
def main():

    # initialize camera
    imageQueue = mp.JoinableQueue(10)
    imageQueue2 = mp.JoinableQueue(10)
    camera = CameraManager(
        [imageQueue, imageQueue2], 
        boardTransport)

    hwclient.spawnBinaryEventStream(
        imageStreamTransport,
        imageQueue,
        encode=lambda i: codec.arrayToTiff(i[1], prefix=i[0]))

    hwclient.spawnBinaryEventStream(
        compressedImageStreamTransport,
        imageQueue2,
        encode=lambda i: codec.arrayToJpg(i[1]//256, prefix=i[0]))

    # # main application loop
    hwclient.HardwareRequestServer( 
        requestTransport, 
        generateCommandTable(camera))


if __name__ == '__main__':
    main()
