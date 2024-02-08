import scriptLoader
import scriptRunner
import beforeAll
import argparse
import asyncio
import os
from orchestrateComponents import orchestrateComponents
import sys
sys.path.insert(0, './common')
import log
import json

logger = log.getLogger('test-bench.main')
logger.info('Started component test-bench')

scripts = scriptLoader.loadScripts()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true',
        help='Run all test scripts')
    parser.add_argument('--name', type=str,
        help='The name of the single script to run')
    args = parser.parse_args()

    if args.name:
        scripts = [next((s for s in scripts if s['name'] in args.name), None)]
        if not scripts:
            print(args.name+' is not a valid test name')

    asyncio.run(beforeAll.run())
    results = asyncio.run(
        orchestrateComponents(scriptRunner.runScript, scripts)
    )
    print(json.dumps(results,indent=4))


'''
--- abstractable components from script call stack ---
component orchestration
test/checkpoint management
timeouts

'''
