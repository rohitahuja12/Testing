import sys
sys.path.insert(0, './common')
import dbclient as db
import asyncio
import contextManagers as ctx
import utils 

tags = ['db','analysis']
requiredComponents = ['db', 'resource-api']


async def execute(checkpoint):

    analysisTemplateBody = { 
        "name": "My analysis!",
        "protocol": "pArray",
        "protocolArgs": {},
    }
    
    # async with ctx.component('db'), ctx.component('resource-api'):

    analysisTemplateId = None

    async with ctx.dbDoc('analysisTemplates', analysisTemplateBody) as a:

        analysisTemplateId = a['_id']
        checkpoint(analysisTemplateId,
            'AnalysisTemplates can be created in db.')

        
        a = await db.get('analysisTemplates', a['_id'])
        checkpoint(a,
            'AnalysisTemplate can be retrieved by document id.')

        await db.update('analysisTemplates', {**a, 'status': 'ERROR', 'errors': ["BOOM"]})
        a = await db.get('analysisTemplates', a['_id'])
        checkpoint(a['status'] == 'ERROR' and a['errors'][0] == "BOOM",
            'Analysis can be updated with "ERROR" status and an error message')

    async def getDoc():
        await db.get('analysisTemplates', analyisId)

    checkpoint(
        await utils.throwsAsync(getDoc),
        'Analysis document is deleted on context manager cleanup')
