import zmq

"""
usage:
    server = sync_request.Server(
        'tcp://localhost:1234', 
        {
            "do_something": lambda: doit()
        }
    )
"""
class Server:

    def __init__(
        self, 
        transport:str, 
        command_table:dict, 
        middlewares:list = [], 
        context:zmq.Context = None,
        encode=None,
        decode=None
    ):
        if context:
            self.context = context
        else:
            self.context = zmq.Context()

        # where to host the server
        self.transport = transport

        # dict of functions and their names
        self.command_table = command_table

        # functions with access to the request and the response
        self.middlewares = middlewares

        self.encode = encode
        self.decode = decode


    def start(self):

        socket = self.context.socket(zmq.REP)
        logger.info(f"Starting request server on {connectStr}")
        socket.bind(self.transport)
        while True:
            try: 
                req = socket.recv()
                decoded_req = self.decode(req) if self.decode else req
                rep = onRequest(decoded_req)
                encoded_rep = self.encode(rep) if self.encode else rep
                socket.send(encoded_rep)
            except Exception as e:
                encoded_err = self.encode(str(e)) if self.encode else str(e)
                socket.send(encoded_err)

    def cleanup(self):
        self.context.term()


class Client:

    def __init__(
        self, 
        transport:str,
        context:zmq.Context = None,
        encode=None,
        decode=None
    ):
        if context:
            self.context = context
        else:
            self.context = zmq.Context()

        self.transport = transport

        self.encode = encode
        self.decode = decode

    def __getattr__(self, key):
        def anon(*args, **kwargs):
            res = 
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
