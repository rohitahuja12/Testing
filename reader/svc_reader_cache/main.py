import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import lib_hardware_interface.client as hwclient
import json
import os
import log 
from readerCache import ReaderCache

logger = log.getLogger("reader.svc_reader_cache.main")

request_transport = os.environ['READER_CACHE_REQUEST_TRANSPORT']

def main():

    def start_cache():
        cache = ReaderCache()

        cmd_table = {
            "help":  lambda: cmd_table,
            **{
                name:getattr(cache, name)
                for name in dir(cache)
                if callable(getattr(cache, name))
                and not name.startswith('__')
            }
        }

        hwclient.HardwareRequestServer(
            request_transport,
            cmd_table
        )
    start_cache()

if __name__ == '__main__':
    main()
