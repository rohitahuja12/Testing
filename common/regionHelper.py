import sys
sys.path.insert(0, './common')
import coords
import log
logger = log.getLogger('common.regionHelper')

'''
given a list of named features from the product definition
take a list of names/points and for each name, resolve
it to its points. Return points unchanged.
'''
def regions(namedRegions):

    def _isPoint(x):
        return x.get('point', False)
    def _isFeature(x):
        return x.get('feature', False)

    def _getRegionPoints(region):
        pts = []
        for ident in region:
            if _isPoint(ident):
                pts.append(ident['point'])
            if _isFeature(ident):
                featureRegion = next((r for r in namedRegions if r['key']==ident['feature']), None)
                if not featureRegion:
                    logger.info('existing regions are: '+str(namedRegions))
                    raise Exception('Failed to resolve point cloud associated with named feature '+
                        str(ident['feature']))
                pts += _getRegionPoints(featureRegion['region'])

        return pts


    def _toPoints(f):
        return lambda x: [coords.Point.fromDict(y) for y in f(x)]

    return _toPoints(_getRegionPoints)


# assuming coords come in xincreasesleft
# and yincreasesup
def pointsToPixelSpace(pts, image):

    maxx = max(pts, key=lambda p: p.x).x
    maxy = max(pts, key=lambda p: p.y).y
    minx = min(pts, key=lambda p: p.x).x
    miny = min(pts, key=lambda p: p.y).y

    featureWidth = maxy - miny
    featureHeight = maxx - minx

    micronsPerPixel = coords.CoordTriplet(
        featureWidth/image.shape[0],
        featureHeight/image.shape[1]
    )

    # make everything relative to top left corner
    pts = [p-coords.Point(maxx, maxy) for p in pts]

    # flip axes to conventional image orientation
    # (x increases right, y increases down)
    pts = [p*coords.Point(-1,-1) for p in pts]

    # to pixel space
    pts = [(p//micronsPerPixel).toInt() for p in pts]

    return pts


