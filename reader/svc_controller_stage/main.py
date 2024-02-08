import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import asyncio
import json
import lib_hardware_interface.client as hwclient
import log
import multiprocessing as mp
import os
from rpc_host import rpc_host
import time
from datetime import datetime as dt
from enum import Enum
from threading import Thread
from readerCacheHelper import getEncodedCachedValueOrRunFetch
import apiClient
from utils.apiAuthProvider import APIAuthProvider

api = apiClient.APIClient(APIAuthProvider())
logger = log.getLogger("controller_stage.main")

mock = os.environ.get('CONTROLLER_STAGE_MOCK', 'false').lower() == 'true'

if mock:
    from mockStageManager import StageManager
    import mock_motor_client as motor_client
else:
    from stageManager import StageManager
    import motor_client

boardTransport = os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']
board_error_stream_transport = os.environ['CONTROLLER_BOARD_ERROR_STREAM_TRANSPORT']
requestTransport = os.environ['CONTROLLER_STAGE_REQUEST_TRANSPORT']
stage_state_stream_transport = os.environ['CONTROLLER_STAGE_MANAGER_STATE_STREAM_TRANSPORT']
stage_manager_state_listener_transport = os.environ['CONTROLLER_STAGE_MANAGER_STATE_LISTENER_TRANSPORT']
motor_client_transport = os.environ['CONTROLLER_STAGE_MOTOR_CLIENT_TRANSPORT']
# motor_client_transport = f'inproc://{motor_client_port}'


def getReader(readerSerial):

    async def _fetch():
        readers = await api.getAll('readers', {'serialNumber':readerSerial})
        if not readers:
            raise Exception(f"Failed to retrieve reader configuration with serial {readerSerial}")
        reader = readers[0]
        return reader

    reader = asyncio.run(getEncodedCachedValueOrRunFetch(
        key = 'reader',
        fetch = _fetch))

    return reader

def getReaderSerial(boardTransport):

    async def _fetch():

        board = hwclient.HardwareClient(boardTransport)
        while True:
            try:
                readerSerial = board.getSerialNumber()
                break
            except Exception as e:
                logger.warn(f'Error connecting to board, retrying. {e}')
                time.sleep(1)
        return readerSerial

    readerSerial = asyncio.run(getEncodedCachedValueOrRunFetch(
        key = 'readerSerial',
        fetch = _fetch))

    return readerSerial


def main():

    get_motor_client = lambda: hwclient.HardwareClient(motor_client_transport)
    board_client = hwclient.HardwareClient(boardTransport)

    # blocks forever
    def start_main_server():
        serial = getReaderSerial(boardTransport)
        reader = getReader(serial)
        logger.info(f'mpmsx: {reader["micronsPerMotorStepX"]}')
        logger.info(f'mpmsy: {reader["micronsPerMotorStepY"]}')

        xyManager = StageManager(
            motorClient=get_motor_client(),
            boardClient=board_client,
            xaddress=1,
            yaddress=2,
            reader=reader
        )

        # initialize motors
        xyManager._setReaderSettings(
            xmicronsPerStep=reader['micronsPerMotorStepX'],
            ymicronsPerStep=reader['micronsPerMotorStepY'],
            xlimitum=reader['stageLimitUmX'],
            ylimitum=reader['stageLimitUmY'],
        )
        cmdtable = {
            "help": lambda: cmdtable,
            **{
                name:getattr(xyManager, name)
                for name in dir(xyManager) 
                if callable(getattr(xyManager, name))
                and not name.startswith('__')
            },
        }
        # blocks forever
        logger.info(f'STARTING STARTING STARTING stage manager server on {requestTransport}')
        hwclient.HardwareRequestServer( 
            requestTransport, 
            cmdtable)


    def start_motor_client():

        thread_motor_client = Thread(
            target=rpc_host, 
            args=(motor_client_transport, motor_client.StageClient()))
        thread_motor_client.start()

    def start_stall_monitor(address):

        def monitor():
            stage_manager_client = hwclient.HardwareClient(requestTransport)
            stage_manager_state_listener = hwclient.HardwareClient(stage_manager_state_listener_transport)
            motor_client = get_motor_client()

            def check_is_running():
                status = motor_client.getMotionStatus(address)
                return 'RUNNING' in status

            def check_stalled():
                passesUnderThreshold = 0
                while True:
                    if not check_is_running():
                        break
                    vel = motor_client.getVelocity(address)
                    if vel < 40:
                        passesUnderThreshold += 1
                        logger.info(f'INCREMENTED PASSES UNDER THRESHOLD: {passesUnderThreshold}')
                    if passesUnderThreshold == 5:
                        logger.info(f'STALL DETECTED! v={vel}')
                        stage_manager_state_listener.stall()
                        motor_client.stop(address)
                        break
                    time.sleep(0)
                        
            while True:
                if check_is_running():
                    check_stalled()
                time.sleep(0.25)

        thread_stall_monitor = Thread(target=monitor)
        thread_stall_monitor.start()

    def start_oob_monitor():
        stage_manager_state_listener = hwclient.HardwareClient(stage_manager_state_listener_transport)
        def monitor():
            for e in hwclient.consumeJsonEventStream(board_error_stream_transport):
                if e['code'] == 9:
                    stage_manager_state_listener.out_of_bounds()

        thread_oob_monitor = Thread(target=monitor)
        thread_oob_monitor.start()


    def start_state_stream():

        streamQueue = mp.JoinableQueue()

        def stream():

            stage_manager_client = hwclient.HardwareClient(requestTransport)

            state = {}
            while True:

                newState = stage_manager_client.get_state()

                if newState != state:
                    state = newState
                    msg = {**state, "timestamp": dt.now().isoformat()}
                    streamQueue.put(msg)

                time.sleep(0.1)

        hwclient.spawnJsonEventStream(
            stage_state_stream_transport,
            streamQueue)

        thread_stream = Thread(target=stream)
        thread_stream.start()


    start_motor_client()
    start_stall_monitor(1)
    start_stall_monitor(2)
    start_oob_monitor()
    start_state_stream()
    #blocks forever
    start_main_server()


if __name__ == '__main__':
    main()
