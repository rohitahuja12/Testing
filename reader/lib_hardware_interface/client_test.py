import time
import unittest
from client import *
from multiprocessing import Process
from threading import Event

class ServerClientTest(unittest.TestCase):

    def throwError(self, error):
        raise error

    def setUp(self):
        self.transport = "tcp://*:9999"
        p = lambda: HardwareRequestServer(
            self.transport,
            {
                "getthree": lambda: 3,
                "throwInternalError": lambda: self.throwError(InternalError()),
                "throwRequestError": lambda: self.throwError(RequestError()),
                "throwOtherError": lambda: self.throwError(Exception('somethingDifferent'))
            })
        self.servProc = Process(target=p)
        self.servProc.start()
        self.client = HardwareClient("tcp://localhost:9999")

    def tearDown(self):
        self.servProc.kill()
        self.servProc.join()

    def testCanPerformRequest(self):
        res = self.client.getthree()
        assert res == 3

    def testCanThrowInternalError(self):
        try:
            self.client.throwInternalError()
        except Exception as e:
            assert isinstance(e, InternalError)
            # pass, exception thrown
            return
        # fail now, call didn't throw
        assert False

    def testCanThrowRequestError(self):
        try:
            self.client.throwRequestError()
        except Exception as e:
            assert isinstance(e, RequestError)
            # pass, exception thrown
            return
        # fail now, call didn't throw
        assert False

    def testCanThrowOtherError(self):
        try:
            self.client.throwOtherError()
        except Exception as e:
            assert isinstance(e, Exception)
            # pass, exception thrown
            return
        # fail now, call didn't throw
        assert False


class MiniMiddleware(Middleware):
    def __init__(self, idnum):
        self.idnum = idnum
    def onRequest(self, req):
        return req + [f'MW{self.idnum}.onRequest']
    def onResponse(self, res):
        return res + [f'MW{self.idnum}.onResponse']


class MiddlewareTest(unittest.TestCase):

    def testCanStackNone(self):
        middleware = CombinedMiddleware([])
        f = lambda *args: list(args) + ['TargetFunction!']
        res = invokeWithMiddleware(f, middleware)(['startin it!'])

    def testCanStackMany(self):
        middleware = CombinedMiddleware([MiniMiddleware(1), MiniMiddleware(2), MiniMiddleware(3)])
        f = lambda *args: list(args) + ['TargetFunction!']
        res = invokeWithMiddleware(f, middleware)(['startin it!'])
        
# def testReqReply():
    # def doWork(r):
        # time.sleep(3)
        # return r

    # spawnRequestServer('tcp://*:5050', doWork)

    # def shout(n):
        # while True:
            # res = request('tcp://localhost:5050', f'from{n}')
            # print(res)

    # p1 = Process(target=shout, args=(1,))
    # p2 = Process(target=shout, args=(2,))
    # p1.start()
    # p2.start()


# def testEventStream():
    # def gen():
        # for i in range(100):
            # yield str(i)
            # time.sleep(1)

    # spawnEventStream('tcp://*:5050', gen)
    # for e in eventStream('tcp://localhost:5050'):
        # logger.info(f'event! {e}')
        # print(e)

# testEventStream()

class PushPullTest(unittest.TestCase):

    def testPushPull(self):
        conn_str = 'ipc://test'
        push = pushClient(conn_str)
        pull = pullClient(conn_str)

        msg = {"a":3}
        push(msg)

        res = pull()
        print(res)
        assert res == msg


if __name__ == "__main__":
    unittest.main()
