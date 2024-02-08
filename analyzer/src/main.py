import asyncio
import io
from zipfile import ZipFile
import sys
sys.path.insert(0, './common')
import os
import heartbeat
from protocolHelper import getProtocols
import apiClient
from apiAuthProviderClientSecret import getAPIAuthProviderClientSecret 
import log

api = apiClient.APIClient(getAPIAuthProviderClientSecret())
logger = log.getLogger('analyzer.src.main')


async def populateContext(context):

    analysis = context['analysis']

    scanId = analysis['scanId']
    scan = await api.get('scans', scanId)

    productId = scan['productId']
    product = await api.get('products', productId)

    scanResultsZip = await api.getAttachment('scans', scanId, 'results')

    def extractZip(zipfiledata):
        b = io.BytesIO(zipfiledata)
        z=ZipFile(b)
        return {name: z.read(name) for name in z.namelist()}
    
    scanResults = extractZip(scanResultsZip)

    # preload scan artifacts storage helper
    async def getScanArtifact(name):
        logger.info(f"Attempting to retrieve scan artifact {name} to process analysis {analysis['_id']}")
        return scanResults[name]

    # preload document artifacts storage helper

    async def createAnalysisArtifact(name, data):
        logger.info(f"Attempting to create analysis artifact {name} "+
                f" for analysis {analysis['_id']}")
        return await api.createAttachment('analyses', analysis['_id'], data, name)

    return {
        **context,
        "analysis": analysis,
        "scan": scan,
        "product": product,
        "getScanArtifact": getScanArtifact,
        "createAnalysisArtifact": createAnalysisArtifact,
        "args": analysis["protocolArgs"]
    }

async def startWorker():

    logger.info('Task worker starting')

    compId = None
    retryPause = 30
    while compId == None:

        try:
            protocols = getProtocols('./analyzer/src/protocols', 'protocols.')
        
            simpleProts = [{'name':p['name'], 'argSchema':p['argSchema']} for p in protocols]
            componentClass = os.environ["COMPONENT_CLASS"]
            logger.info('Registering self and starting component heartbeat')
            comp = await heartbeat.registerAndStartComponentHeartbeat(
                componentClass, {'protocols':simpleProts})
            compId = comp['_id']
            logger.info('Registered self with component id: '+compId)

        except Exception:
            logger.exception('Error connecting to database, retrying in '+str(retryPause)+' seconds.')
            await asyncio.sleep(retryPause)

    while True:

        try:
            queuedAnalyses = await api.getAll('analyses', {'status':'QUEUED'})

            for a in queuedAnalyses:
                s = await api.get('scans', a['scanId'])

                if s.get('results') == 'UPLOADED':
                    await processItem(a, protocols)
        except Exception as e:
            logger.error(f'Error getting analyses {e}')

        await asyncio.sleep(5)

'''
Analyze a single analysis, results will be stored on disk.
Please consult README for instructions.
'''
async def startAnalysisFromDisk():
    pass

async def processItem(analysis, protocols):

    try:
        analysisId = analysis['_id']
        protocolName = analysis['protocol']

        logger.info('Task worker processing analysis '+analysisId)

        await api.update('analyses', {**analysis, 'status': 'RUNNING'})

        # load the protocol specified in the analysis
        protocol = next((x for x in protocols 
            if x['name'] == analysis['protocol']), None)
        if not protocol:
            raise Exception("Specified protocol "+analysis['protocol']+
                " does not exist.")

        # args = analysis.get('protocolArgs',{})

        context = {
            "analysis": analysis
        }

        context = await populateContext(context)

        ################# DOESN'T WORK #################
        # finally validate that the args aren't bogus
        # jsonschema.validate(args, protocol['module'].argSchema)
        ################# DOESN'T WORK #################

        # run protocol and pass all this stuff in
        await protocol['module'].execute(context)

        # update status of analysis
        await api.update('analyses', {**analysis, 'status': 'COMPLETE'})

        logger.info(f"Protocol {protocolName} running analysis {analysisId} complete.")

    except Exception as e:
        msg = f"Error processing analysis {analysisId}. {log.showTrace(e)}"
        logger.error(msg)
        existingErrors = analysis.get('errors',[])
        await api.update(
            'analyses',
            { 
                **analysis,
                'status': 'ERROR',
                'errors': analysis.get('errors',[])+[msg]
            }
        )

if __name__ == "__main__":

    logger.info('Starting analysis worker!')
    asyncio.run(startWorker())


