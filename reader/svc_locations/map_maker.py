import sys
sys.path.insert(0, './reader')
sys.path.insert(0, './common')
import coords 
import json
import plotting

import lib_hardware_interface.client as hwclient
from locationManager import *


def main():
    productPath = sys.argv[1]
    with open(productPath) as p:
        product = json.load(p)
    pts = [
        (
            *galToStage(
                xGal=getBlockCenter(blockData)[0], 
                yGal=getBlockCenter(blockData)[1],
                rotGal=0,
                xAdap=-6748,
                yAdap=101145,
                rotAdap=270,
                xPlateSize=product['sizeX'],
                yPlateSize=product['sizeY'],
                invertAdapterX=True,
                invertAdapterY=False,
                calOffsetX=0,
                calOffsetY=0
            ),
            name
        )
        for name, blockData in product['microArrayBlocks'].items()
    ]
    pts.append((
        *galToStage(
                xGal=0, 
                yGal=0,
                rotGal=0,
                xAdap=-6748,
                yAdap=101145,
                rotAdap=270,
                xPlateSize=product['sizeX'],
                yPlateSize=product['sizeY'],
                invertAdapterX=True,
                invertAdapterY=False,
                calOffsetX=0,
                calOffsetY=0
            ),
        'adapterOrigin'
    ))
    pts.append((
        *galToStage(
                xGal=0, 
                yGal=0,
                rotGal=0,
                xAdap=0,
                yAdap=0,
                rotAdap=270,
                xPlateSize=product['sizeX'],
                yPlateSize=product['sizeY'],
                invertAdapterX=True,
                invertAdapterY=False,
                calOffsetX=0,
                calOffsetY=0
            ),
        'globalAdapterOrigin'
    ))



    # loc = hwclient.HardwareClient("tcp://192.168.1.23:8130")
    # loc.setProduct("641db6e7e9304e17a3b36d31")
    # pts = loc.getAllPoints()
    # pts = [(p['x'], p['y'], p['name']) for p in pts]

    res = plotting.plot([
        plotting.XIncreasesRTL(),
        plotting.YIncreasesTTB(),
        plotting.Point(coords.Point(0,0)),
        *[plotting.Point(coords.Point(p[0],p[1])) for p in pts],
        *[plotting.Text(p[2],p[0],p[1]) for p in pts]
    ])

    sys.stdout.buffer.write(res)

if __name__ == "__main__":
    main()
