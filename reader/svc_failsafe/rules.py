import sys
sys.path.insert(0, './common')
import log

logger = log.getLogger("failsafe.rules")

def doorOpenInHighTorqueMode(state):
    board = state.get('board', None)
    stage = state.get('stage', None)

    if board and stage:
        highTorqX = stage['modeX'] == "highTorque"
        highTorqY = stage['modeY'] == "highTorque"

        return (highTorqX or highTorqY) and board['lidOpen']


"""
prevent stage from hitting front of enclosure

make rules for:
    timeout when homing
    position following error on motor
    in low torque, velocity is zero while attempting to move
    in high torque, door opens
    err_emergency_pwr from board
    timeout from z stage

recovery is restart

in camera:
    separate hardware vs software binning

in stage:
    remove setModeX/setModeY, track and set mode internally
    combine homeX/homeY
    combine stopX/stopY

y near front cover switch should only be tripped if xupperlimit is tripped
"""
