import sys
sys.path.insert(0, './common')
import artifactCodec
import contextManagers as ctx
import json
import asyncio

requiredComponents = []

async def execute(checkpoint):

    codec = artifactCodec.ArtifactCodec()
    
    csvData = [{
        'key1': 3,
        'testkey2': 'hotsauce',
        'k3': None
    },{
        'key1': 8,
        'testkey2': 'eggs',
        'k3': 6.6
    }]
    data = codec.dictArrayToCsv(csvData)
    res = codec.csvToDictArray(data)

    checkpoint(int(csvData[0]['key1']) == int(res[0]['key1']),
        'Dicts can be serialized/deserialized to/from csv')
