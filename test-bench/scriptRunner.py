import asyncio
import beforeAll
import sys
sys.path.insert(0, './common')
import log
import contextManagers as ctx

logger = log.getLogger('test-bench.scriptRunner')

async def runScript(script):
    path = script["name"]
    mod = script["module"]
    res = {
        "name": path,
        "requiredComponents": getattr(mod,'requiredComponents',[]),
        "checkpoints": [],
        "result": ""
    }
    def passTest():
        logger.info(f'RESULT: Test {path} passed.')
        res['result'] = "PASSED" if not res['result'] else res['result']
    def failTest(s):
        logger.error(f'RESULT: Test {path} failed: {s}')
        res['result'] = "FAILED" if not res['result'] else res['result']
        res['error'] = s
    def check(cond, s, details=None):
        res['checkpoints'].append(
            {'name': s, 'passed': not not cond, 'details': details}
        )
        if cond:
            logger.info('Checkpoint passed: ' + s)
        else:
            logger.info('Checkpoint failed: ' + s)
            failTest(s)
    logger.info('Running test:'+path) 

    try:
        await mod.execute(check)
        passTest()
    except Exception as e:
        msg = 'Test threw unhandled exception. See logs for details.'
        logger.exception(msg)
        failTest(msg)

    return res
