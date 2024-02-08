import sys
sys.path.insert(0, './common')
import log
import time

logger = log.getLogger("reader_task_worker.protocols.walk_fairway_perimeter")

async def execute(ctx):
    stage = ctx['stage']

    stage.home()

    # ensure the stage has reached home
    while stage.isMoving():
        time.sleep(0.1)

    homepos = stage.getPosUm()

    def find_max_x():
        lastpos = stage.getPosUm()
        pos = None
        while pos != lastpos:
            lastpos = pos
            stage.jogLeft()
            pos = stage.getPosUm()
        return lastpos[0]

    def find_max_y():
        lastpos = stage.getPosUm()
        pos = None
        while pos != lastpos:
            lastpos = pos
            stage.jogDown()
            pos = stage.getPosUm()
        return lastpos[1]

    min_y = homepos[1]
    max_y = find_max_y()

    min_x = homepos[0]
    max_x = find_max_x()

    logger.info(f'xrange:{min_x, max_x}, yrange:{min_y, max_y}')

    return 
