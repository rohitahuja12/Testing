import sys
sys.path.insert(0, './common')
import lib_hardware_interface.client as hwclient
import log

logger = log.getLogger("controller_stage.rpc_host")

def rpc_host(transport, target_object):
    cmd_table = {
        "help": lambda: table,
        **{
            name:getattr(target_object, name)
            for name in dir(target_object) 
            if callable(getattr(target_object, name))
            and not name.startswith('__')
        },
    }
    logger.info(f'transports going to be: {transport}')
    hwclient.HardwareRequestServer(transport, cmd_table)
