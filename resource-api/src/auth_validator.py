import json
from urllib.request import urlopen
import os
from authlib.oauth2.rfc7523 import JWTBearerTokenValidator
from authlib.jose.rfc7517.jwk import JsonWebKey
from authlib.integrations.flask_oauth2 import ResourceProtector

environment = os.environ.get('ENVIRONMENT', 'dev')

class Auth0JWTBearerTokenValidator(JWTBearerTokenValidator):
    def __init__(self, domain, audience):
        issuer = f"https://{domain}/"
        jsonurl = urlopen(f"{issuer}.well-known/jwks.json")
        public_key = JsonWebKey.import_key_set(
            json.loads(jsonurl.read())
        )
        super(Auth0JWTBearerTokenValidator, self).__init__(
            public_key
        )
        self.claims_options = {
            "exp": {"essential": True},
            "aud": {"essential": True, "value": audience},
            "iss": {"essential": True, "value": issuer},
        }


require_auth = ResourceProtector()
validator = Auth0JWTBearerTokenValidator(
    "dev-zazkmky7c1v5de5q.us.auth0.com",
    f"https://api.{environment}.brightestbio.com"
)
require_auth.register_token_validator(validator)

