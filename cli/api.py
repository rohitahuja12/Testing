import json
import sys
sys.path.insert(0, "./common")
import dbclient
import os
import requests
import time

token_file_path = './cli/token.json'
def get_token():
    with open(token_file_path) as f:
        t = json.load(f)
        return t['access_token']

async def handle (args):

    coll = args["<collection>"]

    if args["create"]:

        fpath = args["<jsonFilePath>"]
        with open(fpath) as f:
            body = json.load(f)

        res = await dbclient.create(coll, body, get_token())
        print(json.dumps(res, indent=True))

    elif args["get"]:

        res = await dbclient.get(coll, args["<docId>"], get_token())
        print(json.dumps(res, indent=True))

    elif args["getall"]:

        fs = args.get("<filters>",None)
        if fs:
            fs = [f.split("=") for f in args["<filters>"].split(',')]
            filters = {f[0]:f[1] for f in fs}
        else:
            filters = {}
        res = await dbclient.getAll(coll, filters, get_token())
        print(json.dumps(res, indent=True))

    elif args["update"]:

        fpath = args["<jsonFilePath>"]
        with open(fpath) as f:
            body = json.load(f)

        res = await dbclient.update(coll, body, get_token())
        print(json.dumps(res, indent=True))

    elif args["delete"]:

        res = await dbclient.delete(coll, args["<docId>"], get_token())
        print(res)

    elif args["login"]:

        # step 1: Request Device Code
        audience = "https://api.dev.brightestbio.com" 
        domain = "dev-zazkmky7c1v5de5q.us.auth0.com"
        client_id = "77fGU0cEyS3DeOpxGCluo83AElIW8jED" # Resource API - Dev
        # client_id = "cOD33J1eFar1Q0it0PhcWUtlRjxC4jsu" # Resource API - Local
        data = { 
            "client_id":client_id, 
            "audience":audience, 
                "scope":"openid offline_access read:readers write:readers read:scans write:scans read:analyses write:analyses read:analysisTemplates write:analysisTemplates read:products write:products read:analysisAttachments write:analysisAttachments read:scanAttachments write:scanAttachments write:featureFlagSets read:featureFlagSets read:defaultPlateMaps write:defaultPlateMaps write:components read:components read:plates write:plates" }
        headers = { 'content-type': "application/x-www-form-urlencoded" }

        res = requests.post(
            f"https://{domain}/oauth/device/code", 
            data=data, 
            headers=headers)

        result = res.json()
        print(result)

        # step 2: Request Device Activation
        print(f"Code: {result['user_code']}")
        print(f"To authenticate, visit this link in a browser: {result['verification_uri_complete']}")

        # step 3: Poll for Request Tokens
        interval = result['interval']
        while True:
            time.sleep(interval)
            data = {
                "device_code": result["device_code"],
                "client_id": client_id,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
            }
            res = requests.post(
                f"https://{domain}/oauth/token",
                data=data,
                headers=headers
            )
            body = res.json()
            if res.status_code == 403 and body['error'] == "authorization_pending":
                continue
            elif res.status_code == 403 and body['error'] == "expired_token":
                print('Token has expired, please try again')
                break
            elif res.status_code == 403 and body['error'] == "access_denied":
                print('Access denied')
                break
            elif res.status_code == 200:
                print('Authenticated! You can now use phx api calls.')
                with open(token_file_path, 'w') as f:
                    f.write(json.dumps(body, indent=4))
                break
