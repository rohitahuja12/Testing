import sys
sys.path.insert(0, './common')
import artifactCodec
import contextManagers as ctx
import json
import asyncio


async def execute(checkpoint):

    codec = artifactCodec.ArtifactCodec()

    jsonData = {
        'key1': 3,
        'testkey2': 'hotsauce',
        'k3': None
    }
    data = codec.dictToJson(jsonData)
    res = codec.jsonToDict(data)

    checkpoint(jsonData['key1'] == res['key1'],
        'Dicts can be serialized/deserialized to/from json')
