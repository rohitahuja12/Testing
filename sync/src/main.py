import sys
sys.path.insert(0, './common')
import timing
import asyncio
import os
import json
from locations.resourceApi import ResourceAPI
from locations.fileSystem import FileSystem
import time
import log

logger = log.getLogger()


jobDir = "./sync/src/jobs"
async def main():

    # load all jobs
    jobs = loadJobs(jobDir)
        
    # start processing them
    for job in jobs:
        
        # source
        jsonSource = job['source']
        jsonSourceType = jsonSource['type'].lower()
        if jsonSourceType == 'filesystem':
            source = FileSystem(jsonSource['path'])
        elif jsonSourceType == 'api':
            source = ResourceAPI(
                jsonSource['host'], 
                jsonSource['documentType'],
                filters=jsonSource.get('filters', None),
                nameField=jsonSource.get('nameField', None))

        # destination
        jsonDest = job['destination']
        jsonDestType = jsonDest['type'].lower()
        if jsonDestType == 'filesystem':
            dest = FileSystem(jsonDest['path'])
        elif jsonDestType == 'api':
            dest = ResourceAPI(
                jsonDest['host'], 
                jsonDest['documentType'],
                filters=jsonDest.get('filters', None),
                nameField=jsonDest.get('nameField', None))

        # build synchronizer function
        def resolveDifferences():
            async def _inner_():
                nonlocal source
                sitems = await source.getItemsList()
                ditems = await dest.getItemsList()
                itemsToSync = findDifferences(sitems, ditems)
                for item in itemsToSync:
                    if item.error:
                        logger.info(f'skipping item because it is broken {item}')
                        continue
                    logger.info(f'synchronizing item with id: {item._id}')
                    data = await source.getItemData(item._id)
                    await dest.createItemData(item.name, data)
            start = time.time()
            asyncio.run(_inner_())
            end = time.time()
            logger.info(f'sync for job {job["_jobName"]} completed in {round(end - start,4)} seconds')

        # run it
        thread = timing.RepeatAction(
            int(job['pollPeriodSeconds']),
            resolveDifferences)

        thread.start()

        


def loadJobs(jobDir):
    jsonFiles = [x for x in os.listdir(jobDir) if x.endswith("json")]
    jobs = []
    for f in jsonFiles:
        fullpath = os.path.join(jobDir, f)
        logger.info(f'f={f} fullpath={fullpath}')
        with open(fullpath) as file:
            job = {**json.load(file), '_jobName': f}
            jobs.append(job)
    return jobs

def findDifferences(sourceItems, destItems):
    pairs = [
        {
            'sourceItem': sourceItem, 
            'destItem': next((destItem for destItem in destItems if destItem._id == sourceItem._id), None)
        } 
        for sourceItem in sourceItems]
    # it is a difference if
    # id exists in source and not in dest
    # or id exists in both but source is newer
    diffs = [
        p['sourceItem'] for p in pairs 
        if p['destItem']==None 
        or p['sourceItem'].lastModified > p['destItem'].lastModified
    ]

    return diffs
    



if __name__ == "__main__":
    asyncio.run(main())
