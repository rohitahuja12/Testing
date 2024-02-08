import sys
sys.path.insert(0, './reader')
sys.path.insert(0, './common')
import coords 
import json
import plotting

import lib_hardware_interface.client as hwclient
from locationManager import *


def main():
    loc = hwclient.HardwareClient("tcp://localhost:8130")
    loc.setProduct("643589c118f4608414de3e44")
    tlpts = loc.getTopLevelPoints()
    # print(f'tlpts: {tlpts}')
    chpts = []
    for pt in tlpts:
        # print(f'point: {pt}')
        try:
            chpts.extend(loc.getChildPoints([*pt['name'],'microArray']))
        except:
            pass
    pts = [(p['x'], p['y'], p['name']) for p in [*tlpts,*chpts]]

    res = plotting.plot([
        plotting.Height(5000),
        plotting.Width(5000),
        plotting.XYScalesEqual(),
        plotting.XIncreasesRTL(),
        plotting.YIncreasesTTB(),
        plotting.Point(coords.Point(0,0)),
        *[plotting.Point(coords.Point(p[0],p[1])) for p in pts],
        # *[plotting.Text(p[2],p[0],p[1]) for p in pts]
    ])

    sys.stdout.buffer.write(res)

if __name__ == "__main__":
    main()
