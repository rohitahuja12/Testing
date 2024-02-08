"""
a feature is a dict of named points
a feature may have children that are also features
when resolving children, locations are summed with parents
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import jsonref as json
import log
logger = log.getLogger('common.productHelper')

@dataclass
class Feature:
    x: int
    y: int
    features: Dict[str, 'Feature']
    attrs: Dict[str, Any]

def parseKitFeatures(kitjson: str) -> Feature:

    kitDict = json.loads(kitjson)

    def featureFromDict(k,featDict):
        children = featDict.get('features', {})
        attrs = featDict.get('attrs', {})
        return Feature(
            x=featDict['x'], 
            y=featDict['y'], 
            features={k:featureFromDict(k,v) for k,v in children.items()},
            attrs=attrs)
    
    features = {k:featureFromDict(k,v) for k,v in kitDict['features'].items()}
    return Feature(x=0,y=0,features=features,attrs={})


# path is like: ["A1","microArray","IL-1alpha_1_3"]
def getFeatureFromPath(featureGraph, path, x=0, y=0):

    assert isinstance(featureGraph, Feature)

    if not path:
        return featureGraph, featureGraph.x + x, featureGraph.y + y
    else:
        try:
            nextfg = featureGraph.features[path[0]]
        except KeyError:
            raise Exception(f"Path item {path[0]} not found.")
        
        return getFeatureFromPath(
            nextfg, 
            path[1:], 
            x+featureGraph.x, 
            y+featureGraph.y)

def getAnalyteSpotMap(productDict):
    features = productDict['relativeFeatures']['microArray']['features']
    analyteSpotMap = {}
    for f in features.values():
        attrs = f['attrs']
        key = ( attrs['row'],attrs['col'] )
        value = attrs['analyte']
        analyteSpotMap[key]=value
    return analyteSpotMap


