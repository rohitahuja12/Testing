import sys
sys.path.insert(0, '.')

import core.logging.log as log
import json
import time
import traceback
import zmq
from core.embedded.hardware_controller.encoders.enumAndFunctionEncoder import EnumAndFunctionEncoder
from core.embedded.hardware_controller.exceptions import InternalError, RequestError

logger = log.getLogger("core.embedded.hardware_controller.server")

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
            socket.send_string(json.dumps(response, cls=EnumAndFunctionEncoder))
        except Exception as e:
            socket.send_string(str(e))

def spawnRequestServer(connectStr, onRequest):
    p = Process(target=runRequestServer, args=(connectStr, onRequest))
    p.start()


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

