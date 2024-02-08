import log
from itertools import permutations
from functools import reduce
import asyncio
logger = log.getLogger('test-bench.orchestrateComponents')
import contextManagers as ctx

neverShutdown = ['db']
async def orchestrateComponents(run, scripts):

    logger.info('optimizing script order!')
    orderedScripts = _optimizeRunOrder(scripts)

    logger.info('optimized script order: '+ str(
        [o for o in orderedScripts]))

    currentComponents = []
    def start(c):
        currentComponents.append(c)
        return ctx.startComponent(c)
    def stop(c):
        currentComponents.remove(c)
        return ctx.stopComponent(c)

    results = []
    for scriptBatch in orderedScripts:

        reqComps = getattr(scriptBatch[0].module, 'requiredComponents', [])
        stops = [stop(c) for c in currentComponents if c not in reqComps and c not in neverShutdown]
        starts = [start(c) for c in reqComps if c not in currentComponents]

        await asyncio.gather(*stops,*starts)

        if 'mock-reader' in currentComponents:
            #sequential
            for script in scripts:
                results.append(await run(script))
        else:
            #concurrent
            res = await asyncio.gather(*[run(s) for s in scripts])
            results.append(res)

    # cleanup all remaining components, we're done here
    logger.info("stopping current components: "+str(currentComponents))
    await asyncio.gather(*[ctx.stopComponent(c) for c in currentComponents])

    return results

# brute force optimize run order
def _optimizeRunOrder(scripts):

    allRequiredComponents = (tuple(sorted(getattr(s.module, 'requiredComponents', []))) 
        for s in scripts)
    uniqSetsRequiredComponents = list(set(allRequiredComponents))

    ps = list(permutations(uniqSetsRequiredComponents))
    # for p in ps:
        # print(_totalToggles(p), p)
    best = min(ps, key=_totalToggles)
    togCnt = _totalToggles(best)
    worstTogCnt = _totalToggles(max(ps, key=_totalToggles))

    orderedScripts = [
        [
            s for s in scripts 
            if set(getattr(s.module, 'requiredComponents', [])) == set(compReqSet)
        ] 
        for compReqSet in best #for s in scripts
    ]
    return orderedScripts

# count the total number of toggles in a given script order
# the componentSet is a given set of components required for
# a group (1 or more) of scripts
def _totalToggles(componentSets):

    def r(acc, cset):
        togs = _countToggles(acc['last'], cset)
        return {
            'total': acc['total']+togs,
            'last': cset
        }
    res = reduce(r, componentSets, {'total': 0, 'last': []})
    return res['total']

# count the number of resources that need switching
# from one list to the next
def _countToggles(xs, ys):
    uniqs = [x for x in xs if x not in ys]
    uniqs += [y for y in ys if y not in xs]
    return len(uniqs)
    
