from enum import Enum

class States(Enum):
    READY = 1 # RTW is accepting tasks
    PROCESSING = 2 # RTW is processing a task, won't accept new tasks
    ERROR = 3 # Something bad has happened, the reader cannot proceed

class Events(Enum):
    GOT_READY = 1
    TASK_STARTED = 2
    TASK_COMPLETED = 3
    TASK_ABORTED = 4
    ERROR_OCCURRED = 5
    ERROR_CLEARED = 6

fsa_graph = {
    States.READY: {
        Events.TASK_STARTED: States.PROCESSING,
        Events.ERROR_OCCURRED: States.ERROR,
    },
    States.PROCESSING: {
        Events.TASK_COMPLETED: States.READY, 
        Events.TASK_ABORTED: States.ERROR,
        Events.ERROR_OCCURRED: States.ERROR
    },
    States.ERROR: {
        Events.ERROR_CLEARED: States.READY,
        Events.ERROR_OCCURRED: States.ERROR
    }
}
