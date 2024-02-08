import sys
import asyncio
sys.path.insert(0, './common')
import artifactCodec
import log

logger = log.getLogger('analyzer.src.protocols.testProtocol1')

argSchema = {
    "type": "object",
    "properties": {
        "argument1": {
            "type": "number"
        }
    }
}

codec = artifactCodec.ArtifactCodec()

async def execute(context):

    logger.info('Running testProtocol1!')

    outputData = [{ "key1": context['args']['argument1'] }]
    await context['createAnalysisArtifact']("test-out.csv", codec.dictArrayToCsv(outputData))
    await context['createAnalysisArtifact']("test-out.json", codec.dictToJson(outputData))
    

