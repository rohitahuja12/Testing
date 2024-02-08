import zmq

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


