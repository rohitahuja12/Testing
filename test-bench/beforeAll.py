import sys
sys.path.insert(0, './common')
import os
import subprocess as sp
import asyncio
import contextManagers as ctx
import log
logger = log.getLogger("test-bench.beforeAll")

async def run():


    components = ['resource-api', 'analyzer','reader','mock-reader']
    logger.info('shutting down the running components we know about')
    
    stops = [ctx.stopComponent(c) for c in components]
    await asyncio.gather(*stops)
    logger.info('finished shutting down all running components')
    
    """
    # os.environ['DB_USER'] = "readeradmin"
    # os.environ['DB_PASSWORD'] = "topsecret"
    # os.environ['DB_HOST'] = "localhost:5984"
    # os.environ['DB_NAME'] = "reader"
    """
