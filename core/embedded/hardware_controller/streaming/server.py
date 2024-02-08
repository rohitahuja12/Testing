import sys
sys.path.insert(0, '.')

import core.logging.log as log
import queue as qlib
import time
import traceback
import zmq
from multiprocessing import Process

logger = log.getLogger("core.embedded.hardware_controller.stream")

"""
generate event streams!!!
"""
def spawnBinaryEventStream(connectStr, queue, encode=lambda x: x):
    def broadcastEventStream():
        context = zmq.Context()
        socket = context.socket(zmq.XPUB)
        socket.set_hwm(10)
        logger.info(f"Starting stream on {connectStr}",)
        socket.bind(connectStr)
        last = None
        while True:

            # maybe publish one from the generator
            try:
                msg = queue.get(block=False)
                queue.task_done()
                # if msg:
                last = msg
                socket.send(encode(msg))
            except qlib.Empty:
                pass
            except Exception as e:
                logger.error(f'Error publishing message {traceback.format_exc()}')

            # maybe someone subscribed and needs last value
            try:
                j = socket.recv(zmq.NOBLOCK)
                if j == b'\x01' and last: # on subscriber join
                    logger.info('found new subscriber, resending last value')
                    socket.send(encode(last))
            except zmq.error.Again:
                pass
            except Exception as e:
                logger.error(f'error getting message {type(e)}:{e}')

            time.sleep(0)

    p = Process(target=broadcastEventStream)
    p.start()

