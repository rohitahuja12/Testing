import sys
sys.path.insert(0, './common')
import requests
import log
import os
from apiTokenTools import getRemainingTokenDuration as getTokenLife

logger = log.getLogger('common.apiAuthProviderClientSecret')

auth_domain = os.environ['AUTH_DOMAIN']
client_id = os.environ['AUTH_CLIENT_ID']
client_secret = os.environ['AUTH_CLIENT_SECRET']
apihost = os.environ['API_URL']


class APIAuthProviderClientSecret:

    def __init__(self, cacheToken=True):
        self.cacheToken = cacheToken
        self.token = None

    def getToken(self):

        def fetchToken():
            logger.info(f'Fetching Token!')
            url = f"https://{auth_domain}/oauth/token"
            res = requests.post(
                url, 
                headers = { 'content-type': "application/x-www-form-urlencoded" },
                data = {
                    'grant_type' : 'client_credentials',
                    'client_id' : client_id,
                    'client_secret' : client_secret,
                    'audience' : f"https://{apihost}"
                })
            body = res.json()
            return body['access_token']

        if self.cacheToken:
            if not self.token or getTokenLife(self.token) < 60:
                self.token = fetchToken()
            return self.token
        else:
            return fetchToken()

    

provider = APIAuthProviderClientSecret()
def getAPIAuthProviderClientSecret():
    return provider

