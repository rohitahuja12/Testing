import sys
sys.path.insert(0, './common')
import lib_hardware_interface.client as hwclient
import threading
import log
import functools

logger = log.getLogger("svc_controller_stage.stage_state_server")
 

def loggit(f):
    @functools.wraps(f)
    def _inner(*args, **kwargs):
        logger.info(f'Stage State Manager received event: {f.__name__}')
        return f(*args, **kwargs)
    return _inner


class StageStateManager:

    def __init__(self):
        self.state = {
            'enabled': True,
            'homed': False,
            'stalled': False,
            'inside': False,
            'inbounds': False,
            'hightorque': False,
            'moving': False,
            'error': False,
            'errorMessage': None,
            'warning': False,
            'warningMessage': None
        }

    @loggit
    def home_start(self):
        self.state['moving'] = True
        self.state['stalled'] = False

    @loggit
    def home_complete(self):
        self.state['homed'] = True
        self.state['moving'] = False
        self.state['inside'] = True
        self.state['inbounds'] = True

    @loggit
    def home_fail(self):
        self.state['moving'] = False

    @loggit
    def move_start(self):
        self.state['moving'] = True

    @loggit
    def move_complete(self):
        self.state['moving'] = False

    @loggit
    def move_fail(self):
        self.state['moving'] = False

    @loggit
    def error(self, msg):
        self.state['error'] = True
        self.state['errorMessage'] = msg

    @loggit
    def error_clear(self):
        self.state['error'] = False
        self.state['errorMessage'] = ''

    @loggit
    def disable(self):
        self.state['enabled'] = False

    @loggit
    def enable(self):
        self.state['enabled'] = True

    @loggit
    def low_torque_mode(self):
        self.state['hightorque'] = False

    @loggit
    def high_torque_mode(self):
        self.state['hightorque'] = True

    @loggit
    def eject_start(self):
        self.state['moving'] = True

    @loggit
    def eject_breach(self):
        self.state['inside'] = False

    @loggit
    def eject_complete(self):
        self.state['moving'] = False

    @loggit
    def eject_fail(self):
        self.state['moving'] = False

    @loggit
    def retract_start(self):
        self.state['moving'] = True

    @loggit
    def retract_complete(self):
        self.state['moving'] = False
        self.state['inside'] = True

    @loggit
    def retract_fail(self):
        self.state['moving'] = False

    @loggit
    def stall(self):
        self.state['stalled'] = True
        self.state['homed'] = False

    @loggit
    def out_of_bounds(self):
        self.state['inbounds'] = False

    def get_state(self):
        return self.state


class StageStateServer:

    def __init__(self, transport):
        self.transport = transport

        self.stage_state_man = StageStateManager()
        cmdtable = {
            "help": lambda: cmdtable,
            **{
                name: getattr(self.stage_state_man, name)
                for name in dir(self.stage_state_man) 
                if callable(getattr(self.stage_state_man, name))
                and not name.startswith('__')
            }
        }

        self.state_listener = threading.Thread(
            target=hwclient.HardwareRequestServer,
            args=(self.transport, cmdtable),
            daemon=True)

    def start(self):
        self.state_listener.start()

