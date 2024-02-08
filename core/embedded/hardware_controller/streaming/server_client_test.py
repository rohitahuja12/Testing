import unittest
import server
import client
import multiprocessing as mp
import time
from threading import Thread

class TestHardwareRequestServer(unittest.TestCase):

    def test_server_and_client(self):

        transport = 'ipc://test'
        queue = mp.JoinableQueue(10)
        message = b"hello"

        t = Thread(
            target=server.spawnBinaryEventStream,
            args=(transport, queue),
            daemon=True
        )
        t.start()

        def sendMsg():
            #janky
            time.sleep(2)
            queue.put(message)
        t2 = Thread(target=sendMsg, daemon=True)
        t2.start()
        
        for msg in client.consumeBinaryEventStream(transport):
            assert msg == message
            break
                


if __name__ == '__main__':
    unittest.main()
