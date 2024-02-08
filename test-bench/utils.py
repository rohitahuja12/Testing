import asyncio

def noThrow(f):
    try:
        f()
        return True
    except:
        return False

def throws(f):
    try:
        f()
        return False
    except:
        return True

async def noThrowAsync(f):
    try:
        await f()
        return True
    except:
        return False

async def throwsAsync(f):
    try:
        await f()
        return False
    except:
        return True

async def callAfterDelay(s, f):
    await asyncio.sleep(s)
    f()

async def callAfterDelayAsync(s, f):
    await asyncio.sleep(s)
    await f()
