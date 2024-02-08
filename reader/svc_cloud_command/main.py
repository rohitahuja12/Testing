import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import asyncio
import apiClient
import lib_hardware_interface.client as hwclient
import log
import os
import subprocess
from utils.apiAuthProvider import APIAuthProvider

logger = log.getLogger('cloud_command.main')

board_transport = os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']
readerSerial = hwclient.HardwareClient(board_transport).getSerialNumber()
task_worker_transport = os.environ['TASK_WORKER_REQUEST_TRANSPORT']

api = apiClient.APIClient(APIAuthProvider())

async def main():
    logger.info("Cloud command is up!")
    rtw_client = hwclient.HardwareClient(task_worker_transport)

    while True:

        task = await retrieveNextTask(readerSerial)

        if task:

            try:
                res = rtw_client.launch_task(task["_id"])
                logger.info(f'Submitted task {task["_id"]} to Reader Task Worker')
            except Exception as e:
                msg = f'Error submitting task {task["_id"]} to Reader Task Worker: {e}'
                logger.info(msg)
                await errorTask(task, msg)

        await asyncio.sleep(10)


async def retrieveNextTask(readerSerialNumber):

    tasks = await api.getAll(
        'scans', 
        {
            'readerSerialNumber':readerSerialNumber,
            'status': 'QUEUED'
        }
    )
    
    if len(tasks) == 0:
        return None

    tasks = sorted(tasks, key=lambda s: s['createdOn'])
    oldestTask = tasks[0]

    return oldestTask


async def errorTask(task, errorMessage):
     
    msg = f"Error processing task {task['_id']} {errorMessage}"
    logger.error(msg)
    existingErrors = task.get('errors',[])
    await api.update(
        'scans',
        { 
            **task,
            'status': 'ERROR',
            'errors': task.get('errors',[])+[msg]
        }
    )


if __name__ == "__main__":
    asyncio.run(main())
