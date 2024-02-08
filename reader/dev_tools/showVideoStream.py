import sys
sys.path.insert(0, '.')
# import cv2
import reader.lib_hardware_interface.client as c
# from datetime import datetime as d
from artifactCodec import ArtifactCodec
codec = ArtifactCodec()
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import numpy
import threading
from queue import Queue

matplotlib.use('TkAgg')
frameStream = Queue()
def ingestFrameStream():
    # host = "localhost"
    host = "192.168.1.24"
    for e in c.consumeBinaryEventStream(f'tcp://{host}:8113'):
        frameStream.put(codec.jpgToArray(e, prefixBytes=4))

threading.Thread(target=ingestFrameStream).start()


fig,ax = plt.subplots(1,1)
image = numpy.array([[1,1,1], [2,2,2], [3,3,3]])
im = ax.imshow(image)

def getLatestFrame():
    # try get first frame
    try:
        latestFrame = frameStream.get(False)
    except:
        return None

    # burn through any additional frames in the queue 
    # until we get the latest
    while True:
        try:
            image = frameStream.get(False)
            latestFrame = image
        except:
            break
    
    return latestFrame


while True:       

    maybeFrame = getLatestFrame()
    if maybeFrame:
        print("frame, yol")
        frameId, frame = maybeFrame
        im.set_data(frame)
        # fig.canvas.draw_idle()

    plt.pause(1)
