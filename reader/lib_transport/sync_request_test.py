import unittest
import sync_request
from threading import Thread 

class SyncRequestTest(unittest.TestCase):

    def setUp(self):
        self.transport_string = 'ipc://test1'
        self.server = sync_request.Server(
            self.transport_string,
            { "add": lambda a, b: a+b }
        )
        
        self.server_thread = Thread(target=self.server.start)
        self.server_thread.start()

        self.client = sync_request.Client(self.transport_string)

    def tearDown(self):
        self.server.cleanup()

    def test_req_rep(self):
        result = self.client.add(1,2)
        assert result == 3




if __name__ == "__main__":
    unittest.main()

