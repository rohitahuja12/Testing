import os
import sys
sys.path.insert(0, './common')
import numpy as np
import unittest
from common.artifactCodec import ArtifactCodec

codec = ArtifactCodec()


class TestArtifactCodec(unittest.TestCase):

    def test_codecJpg(self):
        img = np.zeros((1000,1000))
        jpgImg = codec.arrayToJpg(img)
        resImg = codec.jpgToArray(jpgImg)

    def test_codecJpgWithPrefix(self):
        img = np.zeros((1000,1000))
        prefix = os.urandom(4)
        jpgImg = codec.arrayToJpg(img, prefix=prefix)
        imgId, resImg = codec.jpgToArray(jpgImg, prefixBytes=4)
        assert prefix == imgId

    def test_codecTiff(self):
        img = np.zeros((1000,1000))
        tiffImg = codec.arrayToTiff(img)
        resImg = codec.tiffToArray(tiffImg)

    def test_codecTiffWithPrefix(self):
        img = np.zeros((1000,1000))
        prefix = os.urandom(4)
        tiffImg = codec.arrayToTiff(img, prefix=prefix)
        imgId, resImg = codec.tiffToArray(tiffImg, prefixBytes=4)
        assert prefix == imgId


if __name__ == '__main__':
    unittest.main()
