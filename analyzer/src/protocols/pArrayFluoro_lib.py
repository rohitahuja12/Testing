import utils
import sys
sys.path.insert(0, './common')
sys.path.insert(0, './analyzer/src')
import numpy as np
from statistics import mean
import itertools
from outlierDetector import dixon_test

def transformSpots(spots, transform, key):

    spots = sorted(spots, key=key)
    groups = [list(g) for k, g in itertools.groupby(spots, key)]
    transformedGroups = [transform(g) for g in groups]
    transformedSpots = utils.flatten(transformedGroups)

    return transformedSpots


def addKnownConcentration(spot, initialConcentrations, dilutionFactor):

    if spot['analyte'] in ['POS', 'BLANK']:
        return {
            **spot,
            "knownConcentration":"",
            "seriesIndex":""
        }

    if spot['wellType'] == 'blank':
        return {
            **spot,
            "knownConcentration": 1*10**-10,
            "seriesIndex":""
        }

    if spot['wellType'] == 'standard':
        index = int(spot['wellLabel'].replace("stnd",""))
        ic = float(initialConcentrations[spot['analyte']])
        c = ic/(dilutionFactor**(index-1))
        return {
            **spot,
            "knownConcentration": c,
            "seriesIndex": index
        }

    return spot
def markOutliers(analyteSpots):
    results = analyteSpots
    if (len(analyteSpots) >= 3):
        outlierResultList = dixon_test( [s['intensity'] for s in analyteSpots])
        for a in analyteSpots:
            if a['intensity'] in outlierResultList:
                a['outlier'] = 1
            else:
                a['outlier'] = 0
    return results