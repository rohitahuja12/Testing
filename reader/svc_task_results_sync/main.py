from multiprocessing import Process
import asyncio
import itertools
from datetime import datetime, timedelta
import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import apiClient
from utils.apiAuthProvider import APIAuthProvider

api = apiClient.APIClient(APIAuthProvider())

import log
logger = log.getLogger("task_results_sync.main")
 
import lib_db_task_results.client as taskResultsDb


maxAttempts = 3
def expBackoff(mn, mx):
    return lambda x: min(pow(mn,x),mx)


async def attemptUpload(item):

    try: 
        logger.info(f'Attemping to upload result for task {item["taskId"]}.')

        networkIsUp = await api.pingApi()
        if not networkIsUp:
            # do not attempt
            return

        atts = await api.getAllAttachments('scans', item['taskId'])
        results = [a for a in atts if a['filename'] == 'results']
        attachmentExists = 0 != len(results)
        if attachmentExists:
            attachmentSize = results[0]['size']
            if attachmentSize == item['dataSize']:
                taskResultsDb.updateTask(
                    item['id'], 
                    "EXISTS", 
                    datetime.utcnow().isoformat(), 
                    item['lastAttemptCount'], 
                    None)
                return
            logger.info(f'Attachment named "results" already exists in the database but has size {attachmentSize}. Local item has size {item["dataSize"]}. Deleting existing from database prior to re-attempting.')
            await api.deleteAttachment('scans', item['taskId'], 'results')


        await api.createAttachment(
            'scans',
            item['taskId'],
            item['data'],
            'results')

        # add a field to the main scan doc
        # results: UPLOADED
        await api.update(
            'scans',
            {'_id':item['taskId'], 'results': 'UPLOADED'})


        taskResultsDb.updateTask(
            item['id'],
            "SUCCESS",
            datetime.utcnow().isoformat(),
            item['lastAttemptCount'] + 1 if item['lastAttemptCount'] else 1,
            None)

        logger.info(f'Succeeded uploading result for task {item["taskId"]}.')

    except Exception as e:
        
        if type(item.get('lastAttemptCount', None)) == int and item['lastAttemptCount'] >= maxAttempts:
            logger.info(f'Failed uploading result for task {item["taskId"]}. Attempts exhausted. Final Error: {e}')
            taskResultsDb.updateTask(
                item['id'],
                "FAILED_TOO_MANY_TIMES",
                datetime.utcnow().isoformat(),
                item['lastAttemptCount'] + 1,
                """Upload for this item has failed too many times and will no longer be attempted.
                Final Error: """ + e)
        else:
            logger.info(f'Failed uploading result for task {item["taskId"]}. Will try again later. Error: {e}')
            taskResultsDb.updateTask(
                item['id'],
                "PENDING",
                datetime.utcnow().isoformat(),
                item['lastAttemptCount'] + 1 if item['lastAttemptCount'] else 1,
                "Upload for this item has failed too many times and will no longer be attempted. Error: {e}")


async def process(item):
    logger.info(f"tlat is : {item['lastAttemptTimestamp']}")
    lastAttemptTimestamp = item['lastAttemptTimestamp']

    # if the item has never been attempted, attempt it
    if not lastAttemptTimestamp:
        return await attemptUpload(item)
        

    # if the item has been attempted, only reattempt if
    # enough time has elapsed
    logger.info(f'what is lastAttemptTimestamp?: {lastAttemptTimestamp}')
    lastAttemptTime = datetime.fromisoformat(lastAttemptTimestamp)
    gap = expBackoff(2,100)(item['lastAttemptCount'])
    nextAttemptTime = lastAttemptTime + timedelta(0,gap)
    if nextAttemptTime < datetime.utcnow():
        return await attemptUpload(item)


async def main():

    processes = {}

    while True:
        # retrieve more at a time after development
        items = taskResultsDb.getMany(1)

        for i in items:

            logger.info(f'proceses: {processes}')
            logger.info(f'inspecting item: {i["id"]}')
            p = processes.get(i['id'], None)
            if p and p.is_alive():
                # already processing, skip for now
                continue
            else:
                p = Process(target=lambda: asyncio.run(process(i)))
                processes[i['id']] = p
                p.start()

        # shorten when not in rapid development
        await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(main())



