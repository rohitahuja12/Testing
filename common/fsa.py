from enum import Enum
import multiprocessing as mp
from datetime import datetime as dt
import lib_hardware_interface.client as hwclient
import log
import threading

logger = log.getLogger("common.fsa")

class FSA:

    def __init__(self, graph, initial_state, name):
        self._current_state = initial_state
        self.graph = graph
        self.name = name
    
    def advance(self, event, message):

        try:
            new_state = self.graph[self._current_state][event]
            self._current_state = new_state
        except:
            raise Exception(f"{self.name} {event} {message} is not accepted from state {self._current_state}")

        return self._current_state

    def get_state(self):
        return self._current_state

    def get_legal_events(self):
        return self.graph[self._current_state]


class FSAPublisher:

    def __init__(self, fsa, transport):

        self.fsa = fsa
        self.event_queue = mp.JoinableQueue(25)
        hwclient.spawnJsonEventStream(transport, self.event_queue)
        self.event_queue.put({
            "oldState": None,
            "newState": self.fsa.get_state(),
            "timestamp": dt.utcnow().isoformat(),
        })

    def advance(self, event, message=None):

        old_state = self.fsa.get_state()

        try:
            new_state = self.fsa.advance(event, message)

            msg = {
                "event": event, 
                "eventMsg": message,
                "oldState": old_state,
                "newState": new_state,
                "timestamp": dt.utcnow().isoformat()
            }
            self.event_queue.put(msg)
            return new_state

        except Exception as e:
            self.event_queue.put({
                "event": event, 
                "eventMsg": message,
                "error": str(e),
                "oldState": old_state,
                "newState": self.fsa.get_state(),
                "timestamp": dt.utcnow().isoformat(),
            })
            raise e

    def get_state(self):
        return self.fsa.get_state()

    def get_legal_events(self):
        return self.fsa.get_legal_events()


class FSAServer:

    def __init__(self, fsa, transport, event_enum):
        self.fsa = fsa
        self.transport = transport
        self.event_enum = event_enum

        def signal_event(e, msg=None):
            event = event_enum[e.split('.')[-1]]
            return self.fsa.advance(event, msg)

        handler = {
            "help": lambda: handler,
            "signal_event": signal_event,
            "get_legal_events": self.fsa.get_legal_events,
            "get_state": self.fsa.get_state }

        self.fsa_listener = threading.Thread(
            target=hwclient.HardwareRequestServer,
            args=(self.transport, handler),
            daemon=True)

    def start(self):
        self.fsa_listener.start()

