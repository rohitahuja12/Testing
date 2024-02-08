import sys
import json5 as json
import subprocess
import time
import sys
sys.path.insert(0, './common')
import log
import eventLogging
logger = log.getLogger('orchestrator.main')
event = eventLogging.get_event_logger(logger)

def main():

    configPath = sys.argv[1]
    event('EVENT_ORCHESTRATOR_STARTED')
    logger.info(f'Orchestrator running with config at path {configPath}')

    with open(configPath) as f:
        config = json.load(f)

    processes = config

    # launch all services
    for proc in processes:
        if proc.get("run", False):
            try:
                logger.info(f'Starting service {proc["name"]}')
                proc['process'] = subprocess.Popen(proc['cmd'], shell=True)
            except Exception as e:
                logger.error(f'ORCHESTRATOR WHAM! {e}')

    # continuously look for dead services
    # and restart them
    while True:
        for proc in processes:
            # if process is dead
            if proc.get('run', False) and proc['keepAlive'] == True and proc['process'].poll() is not None:
                logger.info(f'Orchestrator found process {proc["name"]} to be dead. Restarting.')
                proc['process'] = subprocess.Popen(proc['cmd'], shell=True)
        time.sleep(1)
    

if __name__ == '__main__':
    main()
