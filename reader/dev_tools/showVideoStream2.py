import sys
sys.path.insert(0, '.')
import cv2
import reader.lib_hardware_interface.client as c
from artifactCodec import ArtifactCodec
codec = ArtifactCodec()
import numpy as np
import threading
import time
from queue import Queue

# host = "localhost"
host = "192.168.1.24"

frameStream = Queue()
def ingestFrameStream():
    for e in c.consumeBinaryEventStream(f'tcp://{host}:8112'):
        frameStream.put(codec.tiffToArray(e, prefixBytes=4))
threading.Thread(target=ingestFrameStream).start()

# def takeRepeatedExposures():
    # exposure_ms = 1000
    # period_ms = 1500
    # cam = c.HardwareClient(f'tcp://{host}:8110')
    # while True:
        # cam.expose(exposure_ms)
        # time.sleep(period_ms / 1000)
# threading.Thread(target=takeRepeatedExposures).start()


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
