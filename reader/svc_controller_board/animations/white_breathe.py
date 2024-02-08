import sys
sys.path.insert(0, './reader/svc_controller_board')
from math import sin, pi

from animation_frame import AnimationFrame as Frame

frameCt = 16
periodMs = 3000
animDurationMs = 3000

def wave(sampletime, periodms, amplitude):
    val = int((sin((2*pi*sampletime/periodms))+1)/2*amplitude)
    return val

white_breathe = [
    Frame(
        255-wave(x, periodMs, 200),
        255-wave(x, periodMs, 200),
        255-wave(x, periodMs, 200),
        int(animDurationMs / frameCt)
    )
    for x in range(0,animDurationMs-int(animDurationMs/frameCt),int(animDurationMs/frameCt))
]

