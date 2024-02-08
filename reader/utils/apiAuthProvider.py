"""
API Auth Provider for token management. This class to be used on devices.
"""
from readerCacheHelper import cache
import json
import log
import time
import urllib
import auth0.authentication.get_token as auth
from jose import jwk, jwt
from jose.utils import base64url_decode

logger = log.getLogger('reader.utils.apiAuthProvider')

domain = "dev-zazkmky7c1v5de5q.us.auth0.com"
client_id = "77fGU0cEyS3DeOpxGCluo83AElIW8jED" # Resource API - Dev
keys_url = f"https://{domain}/.well-known/jwks.json"

with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

class APIAuthProvider:

    def __init__(self):
        self.cachedTokenKey = 'api_token'
        pass

    def getRemainingTokenDuration(self, token):
        headers = jwt.get_unverified_header(token) 
        kid = headers['kid']
        key_index = -1
        for i in range(len(keys)):
            if kid == keys[i]['kid']:
                key_index = i
                break
        if key_index == -1:
            raise Exception('Public key not found in jwks.json')

        # construct the public key
        public_key = jwk.construct(keys[key_index])

        # get the last two sections of the token,
        # message and signature (encoded in base64)
        message, encoded_signature = str(token).rsplit('.', 1)

        # decode the signature
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))

        # verify the signature
        if not public_key.verify(message.encode("utf8"), decoded_signature):
            return False

        # since we passed the verification, we can now safely
        # use the unverified claims
        claims = jwt.get_unverified_claims(token)

        # additionally we can verify the token expiration
        return claims['exp'] - time.time()

    def refreshCachedToken(self, refreshToken):
        logger.info('Refreshing cached token')
        token_endpoint = auth.GetToken(domain, client_id)
        new_token_blob = token_endpoint.refresh_token(refreshToken)
        new_token_blob = {**new_token_blob, 'refresh_token': refreshToken}
        cache.cacheValue(self.cachedTokenKey, json.dumps(new_token_blob))
        return new_token_blob


    def getToken(self):

        tokenBlob = cache.getCachedValue(self.cachedTokenKey)
        if not tokenBlob:
            raise Exception('No token in cache')

        tokenBlob = json.loads(tokenBlob)
        dur = self.getRemainingTokenDuration(tokenBlob['access_token'])

        if dur <= 60:
            cache.deleteCachedValue('refresh_token_now')
            self.refreshCachedToken(tokenBlob['refresh_token'])
            return self.getToken()

        return tokenBlob['access_token']

