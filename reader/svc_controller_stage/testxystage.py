import sys
sys.path.insert(0, 'reader/lib_hardware_manager/stage')
from xystage import *
import time
import matplotlib.pyplot as plt

s = Stage(1)

def ensureHomingProducesZeroPosition():
    s.sendStageHome()
    time.sleep(1)
    s.setMotorPositionAsOrigin()
    p = s.getPositionSteps()
    print(p)
    assert p == 0

def getPosStepsReturnsSameVal():
    s.home()
    time.sleep(1)
    xs = list(range(10))
    ys = []
    for x in xs:
        print(x)
        s.setPositionSteps(10000, 1000, 100, 100, 0)
        time.sleep(1)
        s.home()
        time.sleep(1)
        ys.append(s.getPositionSteps())

    plt.plot(xs,ys)
    plt.show()
    a = s.getPositionSteps()
    b = s.getPositionSteps()
    c = s.getPositionSteps()
    d = s.getPositionSteps()
    print(a,b,c,d)
    assert a == b
    assert a == c
    assert a == d

def getMotionStatus():
    s.sendStageHome()
    time.sleep(1)
    s.setPositionSteps(100000, 100, 100, 100, 0)
    moving = True
    while moving:
        m = s.getMotorMotionStatus()

def getAlarm():
    s.sendStageHome()
    res = s.getMotorAlarm()
    print(res)

if __name__ == '__main__':

    # ensureHomingProducesZeroPosition()
    # getPosStepsReturnsSameVal()
    # getMotionStatus()
    getAlarm()
