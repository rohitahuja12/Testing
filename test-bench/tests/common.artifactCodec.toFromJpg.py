import sys
sys.path.insert(0, './common')
import artifactCodec
import contextManagers as ctx
import json
import asyncio


async def execute(checkpoint):

    codec = artifactCodec.ArtifactCodec()

    testImg = open('./images/jpgsample.jpg', 'rb').read()
    
    testImg = codec.jpgToArray(testImg)
    res = codec.jpgToArray(codec.arrayToJpg(testImg))

    diff = testImg - res
    checkpoint(
        ((diff+10) < 20).all(),
        'Encoded/decoded jpg image contains sorta the same data as original image. If you want exact same, use tiff.')

