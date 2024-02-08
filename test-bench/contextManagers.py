import sys
sys.path.insert(0, './common')
from contextlib import asynccontextmanager
import subprocess as sp
import asyncio
import dbclient as db
import os
import os.path
import shutil
import log
logger = log.getLogger('test-bench.contextManagers')

# run a cli command async
async def runCmdAsync(cmd):

    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    if stderr:
        logger.error("STDERR running command: " + str(stderr.decode()))
        # raise Exception('bork bork in runCmdAsync '+str(stderr.decode()))

    return stdout.decode()

@asynccontextmanager
async def component(componentName, **kwargs):
    "A phoenix component, usually a docker container"

    try:
        await startComponent(componentName)
        yield True

    finally:
        await stopComponent(componentName)
        if kwargs.get('cleanup', None):
            sp.run(['docker-compose', 'rm', '-v', '-f', componentName])

async def startComponent(componentName):
    await runCmdAsync('docker-compose up -d '+componentName)
    await asyncio.sleep(1)

async def stopComponent(componentName):
    await runCmdAsync('docker-compose stop '+componentName)
    await asyncio.sleep(1)


@asynccontextmanager
async def dbDoc(collection, body):
    "A document in the database"

    try:
        d = await db.create(collection, body)
        yield d

    finally:
        await db.delete(collection, d['_id'])


@asynccontextmanager
async def directory(path):
    "A temporary directory on disk"

    alreadyExisted = True

    try:
        if not os.path.exists(path):
            alreadyExisted = False
            os.mkdir(path) 
        yield path

    finally:
        if not alreadyExisted:
            shutil.rmtree(path)


@asynccontextmanager
async def file(path):
    "A temporary file on disk"

    try:
        with open(path, 'w') as f:
            yield f

    finally:
        os.remove(path)


