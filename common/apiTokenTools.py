import json
import urllib
import os
import time
from jose import jwk, jwt
from jose.utils import base64url_decode

auth_domain = os.environ['AUTH_DOMAIN']
keys_url = f"https://{auth_domain}/.well-known/jwks.json"

with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

def getRemainingTokenDuration(token):

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

