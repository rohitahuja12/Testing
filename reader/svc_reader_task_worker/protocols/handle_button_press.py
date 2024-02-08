import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader/svc_controller_stage')
sys.path.insert(0, '.')
import log
import eventLogging
import time
import stageManager as sm
import apiClient
from reader.utils.apiAuthProvider import APIAuthProvider

logger = log.getLogger("reader_task_worker.protocols.handle_button_press")
event = eventLogging.get_event_logger(logger)
api = apiClient.APIClient(APIAuthProvider())

argSchema = {}

async def execute(ctx):

    stage = ctx['stage']
    board = ctx['board']
    barcode_reader = ctx['barcodeReader']
    invoke_protocol = ctx['invokeProtocol']

    def wait_for_stage_to_stop():
        while stage.get_state()['moving']:
            time.sleep(0.1)
        return

    door_open = board.getIsLidOpen()

    stage_state = stage.get_state()
    logger.info(f'Stage state from handle_button_press {stage_state}')

    if not stage_state['homed'] or not stage_state['inbounds']:
        stage.home()
        wait_for_stage_to_stop()
        return

    if stage_state['inside']:
        stage.eject()
        wait_for_stage_to_stop()
        return

    if not stage_state['inside']:
        stage.retract()
        wait_for_stage_to_stop()

        # read barcode from plate
        barcode = barcode_reader.read()
        
        # if plate inserted
        logger.info(f'Barcode detected! {barcode}')
        if barcode:
            # lookup plate with this barcode
            plates = await api.getAll('plates', {'barcode': barcode})
            logger.info(f'plates with barcode {barcode}: {plates}')
            if len(plates) == 0:
                logger.info(f'no plates match barcode {barcode}, running default product scan.')
                if barcode[:2] == "WP" or barcode[:2] == "5%":
                    return await runDefaultProtocol(ctx, barcode)
                else:
                    logger.error(f"Could not determine product for unknown plate with barcode {barcode}")
                    return
            if len(plates) == 1:
                plate = plates[0]
                scans = await api.getAll('scans', {'plateBarcode': barcode, 'status': 'NOT_QUEUED'})
                scans = [s for s in scans if s['status'] in ['NOT_QUEUED']]
                logger.info(f'scans with plateBarcode {plate["_id"]}: {scans}')
                for scan in scans:
                    await invoke_protocol(taskId=scan['_id'])
                if not scans:
                    return await runDefaultProtocol(ctx, barcode)
            if len(plates) > 1:
                logger.warn(f'Multiple plates match barcode {barcode}')
                return await runDefaultProtocol(ctx, barcode)

    return

async def runDefaultProtocol(ctx, barcode):
    invoke_protocol = ctx['invokeProtocol']
    logger.info(f'Invoking default protocol')
    pargs = {'plateBarcode':barcode}
    return await invoke_protocol(
        protocolName='run_product_default_task', 
        protocolArgs=pargs)

