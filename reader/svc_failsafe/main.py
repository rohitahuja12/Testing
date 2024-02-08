import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import json
import lib_hardware_interface.client as c
import log
import os
import rules
import threading
import zmq
from queue import Queue, Empty

logger = log.getLogger("failsafe.main")

cameraStreamTransport = os.environ['CONTROLLER_CAMERA_STREAM_TRANSPORT']
stageStreamTransport = os.environ['CONTROLLER_STAGE_STREAM_TRANSPORT']
boardStreamTransport = os.environ['CONTROLLER_BOARD_STREAM_TRANSPORT']

boardRequestTransport = os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']
stageRequestTransport = os.environ['CONTROLLER_STAGE_REQUEST_TRANSPORT']

def abort(msg):
    logger.error(f'failsafe detected problem: {msg}. Locking system.')
    board = c.HardwareClient(boardRequestTransport)
    stage = c.HardwareClient(stageRequestTransport)

    stage.stopX()
    stage.stopY()
    board.setLaserAOn(False)
    board.setLaserBOn(False)
    board.setLaserDOn(False)
    # Abort any tasks currently running

    logger.error(f'system locked.')

def main():
    camStreamSck = c.getStreamSocket(cameraStreamTransport)
    boardStreamSck = c.getStreamSocket(boardStreamTransport)
    stageStreamSck = c.getStreamSocket(stageStreamTransport)

    poller = zmq.Poller()
    poller.register(camStreamSck, zmq.POLLIN)
    poller.register(boardStreamSck, zmq.POLLIN)
    poller.register(stageStreamSck, zmq.POLLIN)

    state = {}
    while True:

        addedOne = False
        socks = dict(poller.poll())

        if camStreamSck in socks and socks[camStreamSck] == zmq.POLLIN:
            msg = camStreamSck.recv()
            state['camera'] = json.loads(msg.decode('utf-8'))
            addedOne = True

        if boardStreamSck in socks and socks[boardStreamSck] == zmq.POLLIN:
            msg = boardStreamSck.recv()
            state['board'] = json.loads(msg.decode('utf-8'))
            addedOne = True

        if stageStreamSck in socks and socks[stageStreamSck] == zmq.POLLIN:
            msg = stageStreamSck.recv()
            state['stage'] = json.loads(msg.decode('utf-8'))
            addedOne = True

        if addedOne:
            # uncomment for debuggin'
            # logger.info(json.dumps(state, indent=2))
            res = rules.doorOpenInHighTorqueMode(state)
            if res:
                abort('door opened in high torque mode')





if __name__ == '__main__':
    main()
