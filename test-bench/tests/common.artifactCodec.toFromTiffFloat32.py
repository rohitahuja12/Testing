import sys
sys.path.insert(0, './common')
import artifactCodec
import contextManagers as ctx
import json
import asyncio
import numpy as np


async def execute(checkpoint):

    codec = artifactCodec.ArtifactCodec()

    testImg = np.zeros((1000,1000), dtype=np.float32)
    testImg[0][10]=5.555
    
    data = codec.arrayToTiff(testImg)
    # with open('/phoenix/test-data-output/outImg.tiff', 'wb') as f:
        # f.write(data)
    res = codec.tiffToArray(data)
    checkpoint(res.dtype == np.float32,
        'Encoded/decoded tiff image retains float32 data type.')

    checkpoint(
        np.array(res[0] == testImg[0]).all(),
        'Encoded/decoded tiff image contains the same data as original image')

