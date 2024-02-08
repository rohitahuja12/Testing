import sys
sys.path.insert(0, '.')
import cv2
from core.embedded.hardware_controller.streaming.client import consumeBinaryEventStream
from core.codec.artifact_codec import ArtifactCodec
import numpy as np
import threading
import time
from queue import Queue

codec = ArtifactCodec()

async def handle(args):

    transport = args['<cameraStreamTransport>']

    frameStream = Queue()
    def ingestFrameStream():
        for e in consumeBinaryEventStream(transport):
            frameStream.put(codec.tiffToArray(e, prefixBytes=4))
    threading.Thread(target=ingestFrameStream).start()

    showframe = np.zeros((100,100))
    while True:       

        try:
            framemsg = frameStream.get(block=True, timeout=0.5)
            frameId, showframe = framemsg
        except:
            pass

        # Display the resulting frame 
        aspect_ratio = showframe.shape[1] / showframe.shape[0]
        showframe = cv2.resize(showframe, (1000, round(1000*aspect_ratio)))
        cv2.imshow('Frame', showframe) 
              
        # Press Q on keyboard to exit 
        if cv2.waitKey(25) & 0xFF == ord('q'): 
            break

