import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
sys.path.insert(0, './reader/svc_controller_stage')
sys.path.insert(0, './reader/svc_reader_task_worker')

import lib_hardware_interface.client as hwclient
import log
import os
import time 
import stageManager as sm
import taskManager as tm
logger = log.getLogger("svc_button_handler.main")

board_stream_transport = os.environ['CONTROLLER_BOARD_STREAM_TRANSPORT']
task_worker_request_transport = os.environ['TASK_WORKER_REQUEST_TRANSPORT']
stage_request_transport = os.environ['CONTROLLER_STAGE_REQUEST_TRANSPORT']
board_request_transport = os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']

def main():

    task_worker = hwclient.HardwareClient(task_worker_request_transport)
    stream = hwclient.consumeJsonEventStream(board_stream_transport)
    stage = hwclient.HardwareClient(stage_request_transport)
    board = hwclient.HardwareClient(board_request_transport)

    for event in stream:
        logger.info(event)
        if event['buttonPressed'] == True:

            task_worker_state = tm.States[task_worker.get_state().split('.')[-1]]

            stage_state = stage.get_state()
            task_is_running = task_worker_state == tm.States.PROCESSING
            stage_is_errored = stage_state['error']
            stage_is_moving = stage_state['moving']
            stage_is_disabled = not stage_state['enabled']
            task_is_errored = task_worker.is_errored()
            board_is_errored = board.getEmergencyValue() != 0

            logger.info(f'Task running: {task_is_running}. Stage errored: {stage_is_errored}. Stage moving: {stage_is_moving}. Task errored: {task_is_errored}. Stage disabled: {stage_is_disabled}. Board errored: {board_is_errored}')

            if task_is_running:
                logger.info(f'Button Press triggered kill task')
                task_worker.kill_task()
            
            if stage_is_moving:
                logger.info(f'Button Press triggered disable stage')
                stage.disable()

            if task_is_running or stage_is_moving:
                logger.info('Reader disabled, press button to re-enable')
                continue

            if task_is_errored:
                logger.info(f'Button Press triggered clear task worker error')
                task_worker.clear_error()

            if stage_is_errored:
                logger.info(f'Button Press triggered clear stage error')
                stage.clear_error()

            if stage_is_disabled:
                logger.info(f'Button Press triggered enable stage')
                stage.enable()

            if board_is_errored:
                logger.info(f'Button Press triggered clear board error')
                board.setEmergencyValue(0)

            task_worker.launch_anonymous_task('handle_button_press')


if __name__ == '__main__':
    main()
