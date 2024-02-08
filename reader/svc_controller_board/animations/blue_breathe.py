import sys
sys.path.insert(0, './reader/svc_controller_board')
from math import sin, pi

from animation_frame import AnimationFrame as Frame

frameCt = 16
periodMs = 3000
animDurationMs = 3000

def wave(sampletime, periodms, amplitude, offset):
    val = int(sin((2*pi*sampletime/periodms))*(amplitude/2))+offset
    return val

blue_breathe = [
    Frame(
        0,
        0,
        wave(x, periodMs, 256, 128),
        int(animDurationMs / frameCt)
    )
    for x in range(0,animDurationMs-int(animDurationMs/frameCt),int(animDurationMs/frameCt))
]

