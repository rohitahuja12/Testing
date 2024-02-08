import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import lib_hardware_interface.client as hwclient
import log
import multiprocessing as mp
import os
import time
from threading import Thread
from taskManager import TaskManager, States

logger = log.getLogger("reader_task_worker.main")

task_worker_kill_transport = os.environ['TASK_WORKER_KILL_TRANSPORT']
task_worker_request_transport = os.environ['TASK_WORKER_REQUEST_TRANSPORT']
board_stream_transport = os.environ['CONTROLLER_BOARD_STREAM_TRANSPORT']
rtw_do_initialize = os.environ.get('TASK_WORKER_DO_INITIALIZE', 'true')

"""
run a request server to manage tasks
when a task is created, invoke it in a background process
"""

def main():

    def start_request_server():
        task_manager = TaskManager()

        def _run():

            cmdtable = {
                "help": lambda: cmdtable,
                **{
                    name:getattr(task_manager, name)
                    for name in dir(task_manager) 
                    if callable(getattr(task_manager, name))
                    and not name.startswith('__')
                }
            }
            # blocks forever
            hwclient.HardwareRequestServer( 
                task_worker_request_transport, 
                cmdtable)

        main_thread = Thread(target=_run)
        main_thread.start()

        if rtw_do_initialize.lower() == 'true':
            tmclient = hwclient.HardwareClient(task_worker_request_transport)
            tmclient.launch_anonymous_task('initialize')
            while True:
                s = States[tmclient.get_state().split('.')[-1]]
                if s == States.READY:
                    logger.info('Reader initialized successfully')
                    break
                if s == States.ERROR:
                    logger.error(f'Reader failed to initialize. Check logs.')
                    break

                logger.info('Waiting for initialization to complete.')
                time.sleep(3)

    start_request_server()



if __name__ == '__main__':
    main()



