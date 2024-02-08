import json
import objectpath

def findUniqueValuesForKey(key, data):
    tree = objectpath.Tree(data)
    return list(set(tree.execute('$..'+key)))

def get analyteCoordinateDict(data):
    features = data['features']
    regions = [ feature.get('region') for feature in features ]
    points  = regions[0]
    pointDict = points[0]
    pointDict = [ point['point'] for point in points]
    analyteDict = { (point['row'],point['column']):point['analyte'] for point in pointDict if point['type']=='spot'}
    return analyteDict

def getInitialConcentrations(data):
    initialConcentrations = data['analysisProtocolArgs']['experimentConfiguration']['initialConcentrations']

def computedDilutedConcentration(stndLabel,initialConcentration,dilutionFactor):
    res = 1e-20
    blankString = "BLANK"
    if stndLabel.upper() != blankString:
        #assume label is of format:  stnd7
        try:
            standardNumber = int(stndLabel[4:]) -1
            res = initialConcentration / (dilutionFactor**standardNumber)
        except (TypeError,ValueError):
            res = 0
    return res

def calculateFirstFeature(regions, resolution):
    //regions are the point cloud for a well
    tree = objectpath.Tree(regions)
    extentPoints = list(tree.execute('$.point[@.type is "extent"]'))
    #all control points -> controlPoints = list(tree.execute('$.point[@.analyte is "POS"].(x,y)'))
    #control point at 1,1
    controlPoint = list(tree.execute('$.point[@.row is 1 and @.column is 1].(x,y)'))

