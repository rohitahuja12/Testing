from math import sin, cos, tan

"""
Important variables in this document:

    The values sent to the stage to produce movement to a location
        x_stage
        y_stage

    True spatial coordinates
        x_true
        y_true

    Values after only one correction has been applied (i is for intermediate)
        x_i
        y_i
"""
def stageToTrue(x_stage, y_stage, twist_angle, skew_angle):
    x_i = x_stage - (y_stage * sin(skew_angle))
    y_i = y_stage * cos(skew_angle)
    x_true = (x_i * cos(twist_angle)) - (y_i * sin(twist_angle))
    y_true = (x_i * sin(twist_angle)) + (y_i * cos(twist_angle))
    return (x_true, y_true)

def trueToStage(x_true, y_true, twist_angle, skew_angle):
    x_i = (x_true * cos(twist_angle)) + (y_true * sin(twist_angle))
    y_i = -(x_true * sin(twist_angle)) + (y_true * cos(twist_angle))
    x_stage = x_i + (y_i * tan(skew_angle))
    y_stage = y_i / cos(skew_angle)
    return (x_stage, y_stage)
