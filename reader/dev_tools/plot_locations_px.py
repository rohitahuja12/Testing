import sys
sys.path.insert(0, ".")
sys.path.insert(0, "./common")

import reader.lib_hardware_interface.client as c
import plotting as p
import coords as coords

loc_svc_transport = "tcp://192.168.1.24:8130"
product_id = "649ee5739ce38ab24f003575"
client = c.HardwareClient(loc_svc_transport)

client.setProduct(product_id)
tlpts = client.getTopLevelPoints()
a1array = client.getChildPoints(["A01","microArray"])

print(a1array)
res = p.plot([
    p.Height(5000),
    p.Width(5000),
    p.XYScalesEqual(),
    p.XIncreasesRTL(),
    p.YIncreasesTTB(),
    *[
        p.Point(coords.Point(pt['x'],pt['y']), pt['name'][0])
        for pt in tlpts
    ],
    *[
        p.Point(coords.Point(pt['x']-2200,pt['y']-2200), "TOPLEFT")
        for pt in tlpts
    ],
    *[
        p.Point(coords.Point(pt['x'],pt['y']), pt['name'][0])
        for pt in a1array
    ],
])

with open('out_stage.png', 'wb') as f:
    f.write(res)


res = p.plot([
    p.Height(5000),
    p.Width(5000),
    p.XYScalesEqual(),
    p.XIncreasesLTR(),
    p.YIncreasesTTB(),
    *[
        p.Point(coords.Point(pt['x_px'],pt['y_px']), pt['name'][-1])
        for pt in tlpts
    ],
    *[
        p.Point(coords.Point(pt['x_px'],pt['y_px']), pt['name'][-1])
        for pt in a1array
    ]
])

with open('out_px.png', 'wb') as f:
    f.write(res)
