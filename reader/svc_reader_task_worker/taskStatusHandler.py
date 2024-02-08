import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
sys.path.insert(0, '.')
import log
import apiClient
from reader.utils.apiAuthProvider import APIAuthProvider

api = apiClient.APIClient(APIAuthProvider())

logger = log.getLogger("reader_task_worker.taskStatusHandler")


'''
`taskStatusHandler` manages the status of the task during and after the task is processed by the `processTaskFunc` function.
'''
async def taskStatusHandler(task, processTaskFunc):

    try:
        # change task status to 'RUNNING'
        task = await api.update('scans', {**task, 'status': 'RUNNING'})

        # execute task 
        await processTaskFunc()

        # on successful execution update status to 'COMPLETE'
        task = await api.update('scans', {**task, 'status': 'COMPLETE'})
    
    except Exception as e:
        # on error update status to 'ERROR'
        msg = f"Error processing task {task['_id']}. {log.showTrace(e)}"
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

