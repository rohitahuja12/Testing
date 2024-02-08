import json
import zmq
from core.embedded.hardware_controller.encoders.enumAndFunctionEncoder import EnumAndFunctionEncoder

def jsonRequest(connectStr, req):
    req = json.dumps(req, cls=EnumAndFunctionEncoder)
    response = stringRequest(connectStr, req)
    return json.loads(response)

def stringRequest(connectStr, req):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(connectStr)
    socket.send_string(req)
    res = socket.recv()
    return str(res,'ascii')

class HardwareClient():

    def __init__(self, transport):
        self.transport = transport

    def __getattr__(self, key):
        '''
        provides dot-method access to methods on the controller
        '''
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

