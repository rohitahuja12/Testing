import sys
sys.path.insert(0, '.')
import reader.lib_hardware_interface.client as c
import log

logger = log.getLogger("testbench.cache_tests.main")
cache = c.HardwareClient(f'tcp://localhost:8131')

def testCacheImage():
    with open("test-bench/readerCacheTests/b64TestImage.dat", "r") as f:
      testImage = f.read()
      cache.deleteCachedValue("image")
      cache.cacheValue("image", testImage)
      cachedValue = cache.getCachedValue("image")
      if cachedValue == testImage:
          logger.info("cache test passed")
      else:
          logger.error("cache test failed")

def testUpdateByDoubleEntry():
    cache.cacheValue("test", "val")
    cache.cacheValue("test", "val2")
    cachedValue = cache.getCachedValue("test")
    if cachedValue == "val2":
        logger.info("update by double entry test passed")
    else:
        logger.error("update by double entry test failed")

testCacheImage()
testUpdateByDoubleEntry()