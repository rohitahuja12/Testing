import sys
sys.path.insert(0, './common')
import artifactCodec
import dbclient as db
import contextManagers as ctx
import json
import asyncio
import numpy as np


async def execute(checkpoint):

    codec = artifactCodec.ArtifactCodec()

    testImg = open('./images/pArrayScan.tif', 'rb').read()

    checkpoint(testImg, 'Successfully retrieved testdata tif stack')

    data = codec.tiffStackToArray(testImg)
    res = codec.arrayToTiffStack(data)


    checkpoint(np.array(testImg[0] == res[0]).all(),
        'Encoded/decoded tiff stack images contain same content as original images.')
