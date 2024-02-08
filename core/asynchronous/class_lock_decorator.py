import functools 
import threading
import time

def withClassLock(f):
    @functools.wraps(f)
    def _inner(self, *args, **kwargs):

        threadId = threading.get_ident()

        try:
            self.clientLock
        except:
            self.clientLock = None

        while True:
            if self.clientLock == threadId:
                # lock acquired, begin communicatino
                break
            while self.clientLock != None:
                time.sleep(0)
            self.clientLock = threadId
        try:
            res = f(self, *args, **kwargs)
        finally:
            # release lock
            self.clientLock = None
        return res
    return _inner

