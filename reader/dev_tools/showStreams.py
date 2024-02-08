"""showStreams

Usage:
    showStreams.py <transport>...

"""
from docopt import docopt
import sys
sys.path.insert(0, '.')
import json
import reader.lib_hardware_interface.client as c
import threading
import time
from queue import Queue, Empty

interruptEvent = threading.Event()


def consumeStream(transport, q):
    for e in c.consumeJsonEventStream(transport):
        q.put(e)
        if interruptEvent.is_set():
            break

def mergeQueues(qs, outQueue):
    while not interruptEvent.is_set():
        for q in qs:
            try:
                x = q.get(False)
                if x:
                    outQueue.put(x)
            except Empty:
                pass
            except Exception as e:
                print(e)
        time.sleep(0.01)

def showOutputs(q):
    display = {}
    while not interruptEvent.is_set():
        try:
            msg = q.get(False)
            if msg:
                ### this does merging with prev msg
                # display = {**display, **msg}
                display = msg
                print(json.dumps(display, indent=4))
        except Empty:
            pass
        except Exception as e:
            print(e)
        time.sleep(0.01)

def main(args):
    tqs = [(t, Queue()) for t in args['<transport>']]
    for t, q in tqs:
        threading.Thread(target=consumeStream, args=(t, q)).start()
    outputq = Queue()
    threading.Thread(target=mergeQueues, args=([q for _, q in tqs], outputq)).start()
    threading.Thread(target=showOutputs, args=(outputq,)).start()
    

if __name__ == '__main__':
    try:
        args = docopt(__doc__)
        # time.sleep(21)
        main(args)
    except KeyboardInterrupt:
        interruptEvent.set()
