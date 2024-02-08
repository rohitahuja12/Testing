import json
import sys
sys.path.insert(0, "./common")
import os
import coords as c
from plotting import *

async def handle (args):

    ppath = args["<productPath>"]
    with open(ppath) as f:
        product = json.load(f)

    def find(flimit,key,target):
        flimit(target, key=lambda x: x[key])

    featureBoxes = [
        Box(
            c.Point(
                max(f["region"],key=lambda r:r['point']['x'])['point']['x'],
                max(f["region"],key=lambda r:r['point']['y'])['point']['y']
            ),
            c.Point(
                min(f["region"],key=lambda r:r['point']['x'])['point']['x'],
                min(f["region"],key=lambda r:r['point']['y'])['point']['y']
            ),
            # This will become the label, customize at will
            "".join([str(x) for x in f["key"]])
        )
        for f in product["features"]
    ]

    allPoints = [
        Point(
            c.Point(p['point']['x'], p['point']['y']),
            p['point']['analyte'] if p['point'].get("type",None) == "spot" else ""
        )
        for f in product["features"]
        for p in f["region"]
    ]

    img = plot([
        Title(product["productId"]),
        XIncreasesRTL(),
        YIncreasesBTT(),
        Height(4000),
        Width(4000),
        *featureBoxes,
        *allPoints
    ])

    outPath = args["<outputFilePath>"]
    with open(outPath, 'wb') as f:
        f.write(img)
