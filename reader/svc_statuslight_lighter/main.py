import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
sys.path.insert(0, './reader/svc_controller_stage')
sys.path.insert(0, './reader/svc_reader_task_worker')
import os
from queue import Queue, Empty
import lib_hardware_interface.client as hwclient
import log
import time
import threading
from svc_reader_task_worker.taskManagerFSA import States as taskStates

logger = log.getLogger("svc_statuslight_lighter.main")

board_request_transport = os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']
board_stream_transport = os.environ['CONTROLLER_BOARD_STREAM_TRANSPORT']
stage_stream_transport = os.environ['CONTROLLER_STAGE_MANAGER_STATE_STREAM_TRANSPORT']
rtw_stream_transport = os.environ['TASK_WORKER_STATE_STREAM_TRANSPORT']


WHITE = 0
RED = 1
GREEN = 2
BLUE = 3

def consumeBoardErrors(q, name):
    board = hwclient.HardwareClient(board_request_transport)
    last_value = 0
    while True:
        new_value = board.getEmergencyValue()
        if new_value != last_value:
            last_value = new_value
            q.put((name, last_value))
        time.sleep(1)

def consumeStream(transport, q, name):
    for e in hwclient.consumeJsonEventStream(transport):
        # logger.info(f'LIGHTER EVENT {(name, e)}')
        q.put((name, e))
        # if interruptEvent.is_set():
            # break

def mergeQueues(qs, outQueue):
    while True:
        for q in qs:
            try:
                x = q.get(False)
                if x:
                    outQueue.put(x)
            except Empty:
                pass
            except Exception as e:
                print(e)
        time.sleep(0)


def main(outputq):
    board = hwclient.HardwareClient(board_request_transport)

    current_rtw_state = None
    current_stage_state = None
    current_board_error = None

    while True:
        time.sleep(0)
        try:
            msg = outputq.get(False)
            logger.info(f'GOT A MESSAGE IN LIGHTER: {msg}')
            name, event = msg
        except Empty:
            continue

        if name == 'stage':
            current_stage_state = event
        if name == 'task':
            current_rtw_state = taskStates[event['newState'].split('.')[-1]]
        if name == 'board':
            current_board_error = event

        if current_stage_state:
            if (not current_stage_state['enabled']) \
                    or current_stage_state['stalled'] \
                    or current_stage_state['error']:
                board.setButtonColor(RED)
                continue

        if current_rtw_state in [ taskStates.ERROR ]:
            board.setButtonColor(RED)
            continue

        if current_board_error:
            board.setButtonColor(RED)
            continue

        if current_rtw_state in [ taskStates.READY ]:
            board.setButtonColor(GREEN)
            continue

        if current_rtw_state in [ taskStates.PROCESSING ]:
            board.setButtonColor(BLUE)
            continue


'''

There are several 'animations' stored on the board. Each is structured as the following table:
index, duration, red, green, blue
0, 1000, FF, 00, 00
1, 1000, 00, 00, 00

--- playback pseudocode ---

    while True:
        check the next 2 frames in the circular buffer
        if the first is 'due' and the second is 'notdue':
            play the first frame
            break loop
        else:
            skip the first frame
            continue

--- example commands to create a buffer ---

// Set buffer 1 length to 256:  "_C L 01 00FF." // first 2 digits are buffer id
                                                // last 4 are length

// Set frame 1 red value :      "_C R 01 00FF." // last 2 digits are hex color value
// Set frame 1 blue value :     "_C B 01 00FF."
// Set frame 1 green value :    "_C G 01 00FF."
// Set frame 1 duration value : "_C D 01 A03B." // last 4 digits are hex ms after start

// Set frame 2 red value :      "_C R 02 00FF."
// Set frame 2 blue value :     "_C B 02 00FF."
// Set frame 2 green value :    "_C G 02 00FF."
// Set frame 2 duration value : "_C D 02 A03B."
'''

if __name__ == "__main__":
    board_errors_q = Queue()
    threading.Thread(
        target=consumeBoardErrors, 
        args=(board_errors_q, 'board')
        ).start()

    stage_queue = Queue()
    threading.Thread(
        target=consumeStream, 
        args=(stage_stream_transport, stage_queue, 'stage')
        ).start()
    
    task_queue = Queue()
    threading.Thread(
        target=consumeStream, 
        args=(rtw_stream_transport, task_queue, 'task')
        ).start()

    outputq = Queue()
    threading.Thread(
        target=mergeQueues, 
        args=([board_errors_q, stage_queue, task_queue], outputq)
        ).start()

    main(outputq)
