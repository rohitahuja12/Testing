import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 
import log
logger = log.getLogger('test-bench.tests.analyzer.publishesScriptArgs')

requiredComponents = ['db','resource-api','analyzer']

async def execute(checkpoint):

    checkpoint(True, 'Started analyzer')

    components = await db.getAll('components', {'class':'analyzer'})
    components = list(sorted(components, key=lambda c: c['createdOn']))
    lastComp = components[-1]
    checkpoint(
        'protocols' in lastComp and
        len(lastComp['protocols']) >= 1 and
        lastComp['protocols'][0]['argSchema'], 
        'Analyzer publishes script args')

