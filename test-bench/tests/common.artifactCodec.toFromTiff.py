import sys
sys.path.insert(0, './common')
import artifactCodec
import contextManagers as ctx
import json
import asyncio
import numpy as np


async def execute(checkpoint):

    codec = artifactCodec.ArtifactCodec()

    testImg = open('./images/tiffsample.tif', 'rb').read()
    
    data = codec.tiffToArray(testImg)
    res = codec.arrayToTiff(data)

    checkpoint(
        np.array(res[0] == testImg[0]).all(),
        'Encoded/decoded tiff image contains the same data as original image')

