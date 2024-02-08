import sys
sys.path.insert(0, './common')
import os
import timing

# import dbclient as db
# import heartbeat
import time
from b_continuous_subprocess.continuous_subprocess import ContinuousSubprocess


if __name__ == "__main__":

    # compId = None
    # retryPause = 10
    # while compId == None:

        # try:
            # compId = asyncio.run(heartbeat.registerAndStartComponentHeartbeat(compClass))
            # print('Registered self with component id: '+compId['_id'])

        # except Exception as e:
            # print('Error connecting to database, retrying in '+str(retryPause)+' seconds: ' + str(e))
            # time.sleep(retryPause)

    timeout = int(os.environ['LOG_SHIP_INTERVAL'])
    queue = []

    def write():
        with open('/phoenix/logs/log.txt', 'a') as f:
            f.writeLines(queue)
    timing.RepeatAction(10, write).run()

    while True:
        
        cmd = "docker-compose logs --follow"
        generator = ContinuousSubprocess(cmd).execute()

        for data in generator:
            queue += [data]
    
