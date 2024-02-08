import json
import sys
sys.path.insert(0, "./common")
import dbclient
import os

token_file_path = './cli/token.json'
def get_token():
    with open(token_file_path) as f:
        t = json.load(f)
        return t['access_token']
async def handle (args):

    # assume this is where resource api is running
    os.environ["DB_HOST"] = "localhost:5000"

    scanId = args["<scanId>"]
    outPath = args["<outputDirPath>"]
    attachments = await dbclient.getAllAttachments("scans", scanId,get_token())
    for att in attachments:
        res = await dbclient.getAttachment("scans", scanId, att["filename"],get_token())
        with open(os.path.join(outPath,att["filename"]), "wb") as f:
            f.write(res)
