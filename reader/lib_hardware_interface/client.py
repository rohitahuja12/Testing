import sys
sys.path.insert(0, './common')

import eventLogging
import functools
import inspect
import ujson as json
import json as json_orig
import log
import multiprocessing as mp
import queue as qlib
import time
import types
import zmq
import traceback
from abc import ABC, abstractmethod
from enum import Enum
from multiprocessing import Process

logger = log.getLogger("lib_hardware_interface.client")
event = eventLogging.get_event_logger(logger)


# allow functions and enums to be serialized
class EnumAndFunctionEncoder(json_orig.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return str(obj)
        if isinstance(obj, (types.LambdaType, types.FunctionType, types.MethodType)):
            return "Function: " + obj.__name__ + str(inspect.signature(obj))
        return json_orig.JSONEncoder.default(self, obj)


"""
spawnRequestServer and runRequestServer should be used 
by a server to process requests/responses
"""
def runRequestServer(connectStr, onRequest):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    logger.info(f"Starting request server on {connectStr}")
    socket.bind(connectStr)
    while True:
        message = socket.recv_string()
        try: 
            response = onRequest(json.loads(message))
            socket.send_string(json_orig.dumps(response, cls=EnumAndFunctionEncoder))
        except Exception as e:
            socket.send_string(str(e))

def spawnRequestServer(connectStr, onRequest):
    p = Process(target=runRequestServer, args=(connectStr, onRequest))
    p.start()


"""
request should be used by clients to connect to servers running 'spawnRequestServer'
"""
def jsonRequest(connectStr, req):
    req = json_orig.dumps(req, cls=EnumAndFunctionEncoder)
    response = stringRequest(connectStr, req)
    return json.loads(response)

def stringRequest(connectStr, req):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(connectStr)
    socket.send_string(req)
    res = socket.recv()
    return str(res,'ascii')


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
                if msg:
                    last = msg
                    socket.send(encode(msg))
            except qlib.Empty:
                pass
            except Exception as e:
                logger.error(f'Error publishing message {e}')

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

def spawnStringEventStream(connectStr, queue, encode=lambda x: x):
    return spawnBinaryEventStream(
        connectStr, 
        queue, 
        lambda x: bytes(encode(x), encoding='utf-8'))

# for historical purposes
spawnEventStream = spawnStringEventStream

def spawnJsonEventStream(connectStr, queue):
    return spawnStringEventStream(
        connectStr, 
        queue, 
        encode=lambda x: json_orig.dumps(x, cls=EnumAndFunctionEncoder))



"""
consume<X>EventStream should be used by clients to consume streams
"""
def getStreamSocket(connectStr):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b'')
    socket.set_hwm(10)
    socket.connect(connectStr)
    return socket

def consumeJsonEventStream(connectStr, topic=''):
    return consumeEventStream(connectStr, decode=json.loads, topic=topic)

def consumeEventStream(connectStr, decode=lambda x: x, topic=''):
    socket = getStreamSocket(connectStr)
    while True:
        event = socket.recv_string()
        eventWithoutTopic = event[len(topic):]
        yield decode(eventWithoutTopic)
    
def consumeBinaryEventStream(connectStr, decode=lambda x: x):
    socket = getStreamSocket(connectStr)
    while True:
        event = socket.recv()
        yield decode(event)


"""
PUSH/PULL
"""
def pushClient(connectStr, encode=lambda x: x):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    logger.info(f"PUSH socket running on {connectStr}")
    socket.bind(connectStr)
    def _send(msg):
        msg = encode(msg)
        msg = json_orig.dumps(msg, cls=EnumAndFunctionEncoder)
        socket.send_string(msg)
    return _send

def pullClient(connectStr, decode=lambda x: x):
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect(connectStr)
    def _rcv():
        msg = socket.recv()
        msg = json.loads(msg)
        msg = decode(msg)
        return msg
    return _rcv



class RequestError(Exception):
    pass

class InternalError(Exception):
    pass

class CommandException(Exception):
    pass

class HardwareClient():

    def __init__(self, transport):
        self.transport = transport

    def __getattr__(self, key):
        def anon(*args, **kwargs):
            res = jsonRequest(self.transport, {key: args})
            if 'errorCode' in res[key]:
                code = res[key]['errorCode']
                message = res[key]['message']
                if code.startswith("InternalError."):
                    raise InternalError(code, message)
                elif code.startswith("RequestError."):
                    raise RequestError(code, message)
                raise Exception(code, message)
            else: 
                return res[key]['value']
        return anon

    # def eventStream(self):
        # return consumeEventStream(self.transport


'''
middlewares look like this:

def mw(req, next):
    # do something to the request here,
    res = next(req)
    # do something to the response here
    return res

'''
class Middleware(ABC):
    @abstractmethod
    def onRequest(self, req):
        pass
    @abstractmethod
    def onResponse(self, res):
        pass

class CombinedMiddleware(Middleware):
    def __init__(self, middlewares):
        self.middlewares = middlewares
    def onRequest(self, req):
        for mw in self.middlewares:
            req = mw.onRequest(req)
        return req
    def onResponse(self, res):
        for mw in reversed(self.middlewares):
            res = mw.onResponse(res)
        return res

def invokeWithMiddleware(f, mw):
    def inner(req):
        afterrequest = mw.onRequest(req)
        res = f(*afterrequest)
        return mw.onResponse(res)
    return inner

class HardwareRequestServer():

    def __init__(self, transport, commandTable, middlewares=[]):
        # where to host the server
        self.transport = transport

        # dict of functions and their names
        self.commandTable = commandTable

        # functions with access to the request and the response
        self.middlewares = middlewares

        runRequestServer(
            self.transport, 
            self.handleRequest(self.commandTable, self.middlewares))

    @staticmethod
    def _getSpec(commandTable):
        def cmd_spec(f):
            args = f.__annotations__
            args = {k:v.__name__ if v else v for k,v in args.items()}
            return {'args': args}
        spec = {cmd: cmd_spec(func) for cmd,func in commandTable.items()}
        return spec

    @staticmethod
    def handleRequest(commandTable, middleware=None):
        def handle(req):
            try:
                res = {} 
                for k,v in req.items():
                    try:
                        if k == 'spec':
                            res[k]={'value':HardwareRequestServer._getSpec(commandTable)}
                            continue
                        f = commandTable.get(k)
                        if not f:
                            raise RequestError(CommandException(f"Command '{k}' not recognized"))
                        t1 = time.time()
                        response = invokeWithMiddleware(f, middleware)(v) if middleware else f(*v)
                        t2 = time.time()
                        res[k]={'value': response}
                    except Exception as e:
                        if isinstance(e, InternalError):
                            code = f"InternalError.{e.args[0] if len(e.args)>0 else ''}"
                        elif isinstance(e, RequestError):
                            code = f"RequestError.{e.args[0] if len(e.args)>0 else ''}"
                        else:
                            code = f"UnknownError.{type(e)}"
                        
                        logger.info(f"{e}, {traceback.format_exc()}")
                        res[k]={'errorCode': code, 'message': repr(e)}
                return res
            except Exception as e:
                msg = f'Error handling request {req} : {e}'
                logger.error(msg)
                return {"errorCode": "Exception.RequestHandlingException", "message": msg}
        return handle

