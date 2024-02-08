import unittest
import server
import client
import command_table
from threading import Thread

class TestHardwareRequestServer(unittest.TestCase):

    def test_server_and_client(self):

        def add(a,b):
            return a+b
        table = command_table.CommandTable.fromDict({'add': add})
        transport = 'ipc://test'

        t = Thread(
            target=server.HardwareRequestServer,
            args=(transport, table),
            daemon=True
        )
        t.start()
        
        hwclient = client.HardwareClient(transport)
        result = hwclient.add(1,2)

        assert result==3
        assert hwclient.help()

    def test_command_table_from_object(self):

        class Adder:
            def add(self,a,b):
                return a+b

        table = command_table.CommandTable.fromObject(Adder())
        transport = 'ipc://test'

        t = Thread(
            target=server.HardwareRequestServer,
            args=(transport, table),
            daemon=True
        )
        t.start()
        
        hwclient = client.HardwareClient(transport)
        result = hwclient.add(1,2)

        assert result==3
        assert hwclient.help()


if __name__ == '__main__':
    unittest.main()
