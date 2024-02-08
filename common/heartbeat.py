import sys
sys.path.insert(0, './common')
import requests
import timing
import asyncio
import apiClient
import log
from apiAuthProviderClientSecret import getAPIAuthProviderClientSecret


logger = log.getLogger('common.heartbeat')

api = apiClient.APIClient(getAPIAuthProviderClientSecret())


async def registerAndStartComponentHeartbeat(componentClass, extras={}):

    comp = await api.create('components', {'class':componentClass, **extras})
    compId = comp['_id']

    def x():
        asyncio.run(api.heartbeat('components', compId))

    thread = timing.RepeatAction(5, x) 
    thread.start()

    return comp
    

