import sys
sys.path.insert(0, './common')
import time

import log

logger = log.getLogger("reader_task_worker.moveto")

argSchema = {
    'type': 'object',
    'properties': {
        'feature': {
            'type': 'array',
            'description': 'The product feature to which to move the stage'
        }
    }
}

async def execute(ctx):
    stage = ctx['stage']
    locations = ctx['locations']
    feature = ctx['args']['feature']
    
    locations.setProduct(ctx['task']['productId'])
    featureName = ''.join([feature[1],feature[2].zfill(2)])

    pt = locations.getPoint([featureName])
    camCenter = locations.getPoint("cameraCenter")
    
    destx = camCenter['x'] - pt['x']
    desty = camCenter['y'] - pt['y']
    logger.info(f'moving to: {(destx, desty)}')
    stage.move(destx, desty)

    return
