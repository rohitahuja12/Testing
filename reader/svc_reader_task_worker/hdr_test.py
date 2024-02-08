import sys
sys.path.insert(0, '.')

import unittest
import numpy as np

from hdr import hdrSum
import core.logging.log as log

logger=log.getLogger('reader.svc_reader_task_worker.hdr_test')

imgW = 5 # image width > 4
imgH = 4 # image height > 3
imgN = 3  # number of images in the stack > 2

def generate_image_stack():
    # generate a stack of imgN images shaped (imgH,imgW)
    # The corresponding durations are 1,2,...,imgN
    imgs = []
    for nn in range(1,imgN+1):
        img = np.full(shape=(imgH,imgW), fill_value=0, dtype=np.uint16)
        dur = nn
        for ww in range(imgW):
            for hh in range(imgH):
                img[hh][ww] = (1+ww+1+hh)*dur
        imgs.append((img,dur))
    # add saturated values at (3,2) in the last two images
    (img,dur) = imgs[-2]
    img[3][2]=generate_sat_value()
    (img,dur) = imgs[-1]
    img[3][2]=generate_sat_value()+1
    return imgs

    
def generate_hdr_result():
    result = np.full(shape=(imgH,imgW), fill_value=0, dtype=np.float32)
    for ww in range(imgW):
        for hh in range(imgH):
            result[hh][ww] = (1+ww+1+hh)*(imgN+1)*imgN/2
    return result

def generate_sat_value():
    return (imgW+imgH)*imgN+1


class TestHdr(unittest.TestCase):

    def test_hdr_sum(self):
        input = generate_image_stack()
        output1 = generate_hdr_result()
        sat = generate_sat_value()
        output2 = hdrSum(input,sat) # run with sat+1 to fail the test
        assert (np.all(output1 == output2))

if __name__ == "__main__":
    unittest.main()
