import sys
sys.path.insert(0, './common')

import log

logger = log.getLogger("reader_task_worker.pfluoro")

argSchema = {
    'type': 'object',
    'properties': {}
}

async def execute(ctx):
    """
    do pfluoro here
    """
    af_result = await ctx['protocols']['autofocus']['module'].execute(ctx)

