import sys
sys.path.insert(0, './common')
import asyncio
import fsa
import lib_hardware_interface.client as hwclient
import log
import multiprocessing as mp
import os
import processor
import threading
import time
import traceback
from protocolHelper import getProtocolsDict
from taskManagerFSA import States, Events, fsa_graph
logger = log.getLogger("svc_reader_task_worker.taskManager")


task_worker_state_stream_transport = os.environ['TASK_WORKER_STATE_STREAM_TRANSPORT']
rtw_state_listener_transport = os.environ['TASK_WORKER_TASK_STATE_LISTENER_TRANSPORT']


class TaskManager:

    def __init__(self):
        self.task_process = None
        self.fsa = fsa.FSAPublisher(
            fsa.FSA(fsa_graph, States.READY, "TaskManager"),
            task_worker_state_stream_transport
        )
        self.fsa_listener = fsa.FSAServer(
            self.fsa, 
            rtw_state_listener_transport,
            Events)
        self.fsa_listener.start()

    def _get_fsa_client(self):
        return hwclient.HardwareClient(rtw_state_listener_transport)

    def launch_task(self, taskId:str) -> str:

        protocols = getProtocolsDict(
            'reader/svc_reader_task_worker/protocols', 
            'protocols.'
        )
        def _run():
            try:
                asyncio.run(processor.main(protocols, taskId=taskId))
                self._get_fsa_client().signal_event(Events.TASK_COMPLETED)
            except Exception as e:
                msg = f"{e}, {traceback.format_exc()}"
                logger.info(msg)
                self._get_fsa_client().signal_event(Events.ERROR_OCCURRED, msg)

        self._get_fsa_client().signal_event( Events.TASK_STARTED, {'taskId':taskId})
        self.task_process = mp.Process(target=_run)
        self.task_process.start()
        return taskId

    def launch_anonymous_task(self, name:str) -> bool:

        protocols = getProtocolsDict(
            'reader/svc_reader_task_worker/protocols', 
            'protocols.'
        )
        def _run():
            try:
                asyncio.run(processor.main(protocols, protocolName=name))
                self._get_fsa_client().signal_event(Events.TASK_COMPLETED)
            except Exception as e:
                msg = f"{e}, {traceback.format_exc()}"
                logger.info(msg)
                self._get_fsa_client().signal_event(Events.ERROR_OCCURRED, msg)

        self._get_fsa_client().signal_event( Events.TASK_STARTED, {'name':name})
        self.task_process = mp.Process(target=_run)
        self.task_process.start()
        return True

    def kill_task(self):

        self._get_fsa_client().signal_event(Events.TASK_ABORTED)

        self.task_process.terminate()
        time.sleep(0.1)
        if not self.task_process.is_alive():
            logger.info("Killed process")
            self.task_process.join(timeout=1.0)

    def clear_error(self):
        return self._get_fsa_client().signal_event(Events.ERROR_CLEARED)

    def get_state(self):
        return self.fsa.get_state()

    def is_errored(self):
        return self.get_state() == States.ERROR


