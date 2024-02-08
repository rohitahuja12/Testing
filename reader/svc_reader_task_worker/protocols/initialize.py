import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader/svc_controller_stage')

import os
import log
import stageManager
import time
logger = log.getLogger('reader_task_worker.protocols.initialize')

async def execute(ctx):
    def stage_is_homed():
        return ctx['stage'].get_state()['homed']

    if not stage_is_homed():
        ctx['stage'].home()

        while not stage_is_homed():
            time.sleep(0.1)
    
