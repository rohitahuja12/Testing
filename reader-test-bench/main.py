import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
from dateutil.parser import parse
import datetime
import docker
import lib_hardware_interface.client as hwclient
import log
import os
import time

logger = log.getLogger("reader_test_bench.main")
boardTransport = 'tcp://127.0.0.1:8120' # os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']
# stagePort = 8100
taskWorkerTransport = 'tcp://127.0.0.1:8140'
boardClient = hwclient.HardwareClient(boardTransport)
task_worker = hwclient.HardwareClient(taskWorkerTransport)
# stageClient = hwclient.HardwareClient(f'tcp://localhost:{boardPort}')

client = docker.from_env()
containers = client.containers.list()
reader_container = next(c for c in containers if "reader" in c.name)

def get_event_logs():
    logs = reader_container.logs().decode().split('\n')
    event_logs = [ l for l in logs if "EVENT" in l ]
    return event_logs

def time_button_press_to_event_start(iterations):
    def time_one():
        boardClient._setButtonPressed(True)
        time.sleep(5)
        event_logs = list(reversed(get_event_logs())) # reverse to look at newest first
        press = next(e for e in event_logs if 'EVENT_MAIN_BUTTON_PRESSED' in e)
        compl = next(e for e in event_logs 
            if ('EVENT_STAGE_EJECTING' in e
            or 'EVENT_STAGE_RETRACTING' in e))
        presstimestr = press.split('[')[0]
        presstime = parse(presstimestr)
        compltime = parse(compl.split('[')[0])
        print (f'Time between button press and eject: {compltime-presstime}')
        return compltime-presstime
    times = [time_one() for _ in range(0, iterations)]
    avgtime = sum(times, datetime.timedelta()) / iterations
    return avgtime

def time_parray_to_stage_move(iterations):
    def time_one():
        is_running = task_worker.get_task_is_running()
        if is_running:
            task_worker.kill_task()
        task_worker.launch_task('648c995d9ce38ab24f0033a0') # reader 3, parray, newest infla kit
        time.sleep(10)
        event_logs = list(reversed(get_event_logs())) # reverse to look at newest first

        # skip if event_logs is empty
        if len(event_logs) == 0:
            return datetime.timedelta() # sample: 0:00:00
        start = next(e for e in event_logs if 'EVENT_PARRAY_START' in e)
        compl = next(e for e in event_logs if 'EVENT_STAGE_MOVING' in e)
        starttimestr = start.split('[')[0]
        starttime = parse(starttimestr)
        compltime = parse(compl.split('[')[0])
        print (f'Time between parray start and stage moving: {compltime-starttime}')
        return compltime-starttime
    times = [time_one() for _ in range(0, iterations)]
    avgtime = sum(times, datetime.timedelta()) / iterations
    return avgtime

def main():
    # avgtime = time_button_press_to_event_start(10)
    # print(f'Average time between button press and eject: {avgtime}')

    avgtime = time_parray_to_stage_move(10)
    print(f'Average time between parray start and stage moving: {avgtime}')

# start scan -> stage moving? perhaps

if __name__ == '__main__':
    main()

