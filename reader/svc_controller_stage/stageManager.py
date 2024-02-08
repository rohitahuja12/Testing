"""
This source file is responsible for handling 
incoming requests and for producing an event
stream.
"""
import sys
sys.path.insert(0, './common')
import asyncio
import eventLogging
import fsa
import lib_hardware_interface.client as hwclient
import log
import numpy as np
import os
import time
import traceback
import functools
import twist_corrector
import artifactCodec
from readerCacheHelper import getCalibrationValue
from enum import Enum
from threading import Thread
from motor_client import MotionStatus
from typing import Dict, List
from stage_state_server import StageStateServer

codec = artifactCodec.ArtifactCodec()
logger = log.getLogger("svc_controller_stage.stageManager")
event = eventLogging.get_event_logger(logger)

stage_manager_state_stream_transport = os.environ['CONTROLLER_STAGE_MANAGER_STATE_STREAM_TRANSPORT']
stage_manager_state_listener_transport = os.environ['CONTROLLER_STAGE_MANAGER_STATE_LISTENER_TRANSPORT']


class StageException(Exception):
    pass

def state_require(*requirements):
    def _decorator(f):
        @functools.wraps(f)
        def _inner(self, *args, **kwargs):
            state = self.get_state()
            for req in requirements:
                if not state[req]:
                    raise StageException(f'Cannot perform operation {f.__name__}, it requires {req}.')
            f(self, *args, **kwargs)
        return _inner
    return _decorator

def state_forbid(*requirements):
    def _decorator(f):
        @functools.wraps(f)
        def _inner(self, *args, **kwargs):
            state = self.get_state()
            for req in requirements:
                if state[req]:
                    raise StageException(f'Cannot perform operation {f.__name__}, it forbids {req}.')
            f(self, *args, **kwargs)
        return _inner
    return _decorator

"""
StageManager is a wrapper around the stage that takes care of origin-based
step offsets, initialization.
StageManager should only ever be called from one thread, and its stage should 
never be called from anywhere but this file.
"""
class StageManager():

    def __init__(
        self, 
        motorClient,
        boardClient,
        xaddress,
        yaddress,
        reader):

        self.motorClient = motorClient
        self.boardClient = boardClient
        self.xaddress = xaddress
        self.yaddress = yaddress
        self.reader = reader
        self.xorigin = None # will be used to correct positions from the stage
        self.yorigin = None

        self.validateBounds = True # ONLY SET THIS TO FALSE IN DEBUG!!!!
        self.correctTwist = True

        self.homed = False
        self.homingHighVel = 600
        self.homingLowVel = 50
        self.homingAcc = 100
        self.homingDec = 100
        self.lowTorqueVel= 600 
        self.lowTorqueAcc = 500
        self.lowTorqueDec = 500
        self.lowTorquePeakCurrent = 7
        self.highTorquePeakCurrent = 28
        self.highTorqueVel= 600
        self.highTorqueAcc = 100
        self.highTorqueDec = 100

        # this setting changes how deep the stage travels into the optical limit switches
        # at the edges of the fairway
        self.motorClient.setQuickStopTimeMs(1, 300)
        self.motorClient.setQuickStopTimeMs(2, 300)

        self.stage_state_listener = StageStateServer(
            stage_manager_state_listener_transport)

        self.stage_state_listener.start()

    def _get_state_listener(self):
        return hwclient.HardwareClient(stage_manager_state_listener_transport)

    def get_state(self):
        return self._get_state_listener().get_state()

    @state_require('enabled')
    @state_forbid('error', 'moving')
    def home(self, resetOriginOffset:bool=True) -> bool:

        def _home():
            try:
                state = self.get_state()
                if not state['inbounds']:
                    self.boardClient.setMonitorTrayPosition(False)
                    time.sleep(1)
                self._setLowTorqueMode(True)
                self.motorClient.setHomingHighVelocity(1, self.homingHighVel)
                self.motorClient.setHomingHighVelocity(2, self.homingHighVel)
                self.motorClient.setHomingLowVelocity(1, self.homingLowVel)
                self.motorClient.setHomingLowVelocity(2, self.homingLowVel)
                self.motorClient.setHomingAcc(1, self.homingAcc)
                self.motorClient.setHomingAcc(2, self.homingAcc)
                self.motorClient.setHomingDec(1, self.homingDec)
                self.motorClient.setHomingDec(2, self.homingDec)
                logger.info('homing y, then x')
                self.motorClient.sendStageHome(self.yaddress)
                self._blockUntilStopped()

                # # stopped bcause of disable, quit now
                state = self.get_state()
                if not state['enabled'] or state['error'] or state['stalled']:
                    return self._get_state_listener().home_fail()

                self.motorClient.sendStageHome(self.xaddress)
                self._blockUntilStopped()

                # if stopped because of disable, quit now
                state = self.get_state()
                if not state['enabled'] or state['error'] or state['stalled']:
                    return self._get_state_listener().home_fail()

                if resetOriginOffset:
                    self.xorigin = np.uint32(self.motorClient.getPosSteps(self.xaddress))
                    self.yorigin = np.uint32(self.motorClient.getPosSteps(self.yaddress))
                    
                self._setLowTorqueMode(False)
                # if stage was disabled during run, don't complete
                state = self.get_state()
                if state['enabled'] and not state['error'] and not state['stalled']:
                    self.boardClient.setMonitorTrayPosition(True)
                    self._get_state_listener().home_complete()
                else:
                    self._get_state_listener().home_fail()
            except Exception as e:
                msg = f"Error while homing: {e}, {traceback.format_exc()}"
                logger.info(msg)
                self._get_state_listener().home_fail()
                self._get_state_listener().error(msg)


        self._get_state_listener().home_start()
        t = Thread(target=_home)
        t.start()
        return True

    @state_require('enabled', 'homed', 'inside', 'inbounds')
    @state_forbid('error', 'stalled', 'moving')
    def move(self, xposition:int, yposition:int) -> bool:

        def _move():
            try:
                assert self.boardClient.getMonitorTrayPosition()

                logger.info("Stage attempting move to {(xposition, yposition)}")
                self._setPosUm(xposition,yposition)
                self._blockUntilStopped()

                # stopped because of disable, quit now
                state = self.get_state()
                if not state['enabled'] or state['error'] or state['stalled']:
                    return self._get_state_listener().move_fail()

                self._get_state_listener().move_complete()
            except Exception as e:
                msg = f"{e}, {traceback.format_exc()}"
                logger.info(msg)
                self._get_state_listener().move_fail()
                self._get_state_listener().error(msg)

        self._get_state_listener().move_start()
        t = Thread(target=_move)
        t.start()
        return True

    @state_require('enabled', 'homed', 'inside', 'inbounds')
    @state_forbid('error', 'stalled', 'moving')
    def eject(self) -> bool:

        def _eject():
            try:
                assert self.boardClient.getMonitorTrayPosition()

                # disable twist correction, ejecting is not a precise movement
                # and we want it to function when the reader is not calibrated
                correctTwist = self.getCorrectTwist()
                self.setCorrectTwist(False)

                # move to the front corner of the fairway
                self._setPosUm(self.xlimitum, self.ylimitum)
                self._blockUntilStopped()

                # restore twist correction
                self.setCorrectTwist(correctTwist)
                
                # stopped because of disable, quit now
                state = self.get_state()
                if not state['enabled'] or state['error'] or state['stalled']:
                    return self._get_state_listener().eject_fail()

                self._get_state_listener().eject_breach()

                # start low-torque moddisable
                self._setLowTorqueMode(True)
                
                # eject tray
                pos = self.motorClient.getPosSteps(self.yaddress)
                logger.info(f'current ypossteps = {pos}')
                logger.info(f'ejectedYLimitUm = {self.ejectedYLimitUm}')
                self.motorClient.setPosSteps( 
                    self.yaddress,
                    self.ejectedYLimitUm, 
                    self.lowTorqueVel, 
                    self.lowTorqueAcc,
                    self.lowTorqueDec, 
                    0)

                while True:
                    # get position and velocity
                    status = self.getMotionStatus()
                    if MotionStatus.RUNNING.name not in [*status['x'],*status['y']]:
                        # if stage was disabled during run, don't complete
                        state = self.get_state()
                        if not state['enabled'] or state['error'] or state['stalled']:
                            self._get_state_listener().eject_fail()
                        else:
                            self._get_state_listener().eject_complete()
                        break 
                    time.sleep(0)

            except Exception as e:
                msg = f"{e}, {traceback.format_exc()}"
                logger.info(msg)
                self._get_state_listener().eject_fail()
                self._get_state_listener().error(msg)

        self._get_state_listener().eject_start()
        t = Thread(target=_eject)
        t.start()
        return True

    @state_require('enabled', 'homed', 'inbounds')
    @state_forbid('error', 'stalled', 'moving', 'inside')
    def retract(self):

        def _retract():

            try:
                assert self.boardClient.getMonitorTrayPosition()

                self._setLowTorqueMode(True)
                # move to the front corner of the fairway
                ypositionSteps = round(self.ylimitum / self.ymicronsPerStep)
                self.motorClient.setPosSteps(
                    self.yaddress, 
                    ypositionSteps, 
                    self.lowTorqueVel, 
                    self.lowTorqueAcc, 
                    self.lowTorqueDec, 
                    0)

                self._blockUntilStopped()
                # stopped because of disable, quit now
                state = self.get_state()
                if not state['enabled'] or state['error'] or state['stalled']:
                    return self._get_state_listener().retract_fail()

                self._setLowTorqueMode(False)
                self._get_state_listener().retract_complete()

            except Exception as e:
                msg = f"{e}, {traceback.format_exc()}"
                logger.info(msg)
                self._get_state_listener().retract_fail()
                self._get_state_listener().error(msg)

        self._get_state_listener().retract_start()
        t = Thread(target=_retract)
        t.start()
        return True

    def clear_error(self):
        self._get_state_listener().error_clear()
        self.motorClient.setMotionDisabled(False)
        return

    def _setReaderSettings(
        self,
        xmicronsPerStep, 
        ymicronsPerStep,
        xlimitum,
        ylimitum):

        self.xmicronsPerStep = xmicronsPerStep
        self.ymicronsPerStep = ymicronsPerStep
        self.xlimitum = xlimitum # pair of lower/upper Um x values describing the 'fairway'
        self.ylimitum = ylimitum
        self.ejectedYLimitUm = 2205000

    def _setLowTorqueVel(self, v:int) -> int :
        self.lowTorqueVel = v

    def _getLowTorqueVel(self) -> int:
        return self.lowTorqueVel

    def _setLowTorqueAcc(self, v:int) -> int:
        self.lowTorqueAcc = v

    def _getLowTorqueAcc(self) -> int:
        return self.lowTorqueAcc

    def _setLowTorqueDec(self, v:int) -> int:
        self.lowTorqueDec = v

    def _getLowTorqueDec(self) -> int:
        return self.lowTorqueDec

    def setCorrectTwist(self, correct:bool) -> bool:
        self.correctTwist = correct
        return correct

    def getCorrectTwist(self) -> bool:
        return self.correctTwist

    def _blockUntilStopped(self) -> bool:
        while True:
            status = self.getMotionStatus()
            if MotionStatus.RUNNING.name not in [*status['x'],*status['y']]:
                break
            time.sleep(0)
        return True

    def getBounds(self) -> dict:
        return {"x":self.xlimitum,"y":self.ylimitum}

    def getMicronsPerStep(self) -> dict:
        return {"x":self.xmicronsPerStep,"y":self.ymicronsPerStep}

    def _setMicronsPerStep(self, xmicronsPerStep: float, ymicronsPerStep: float) -> dict:
        self.xmicronsPerStep = xmicronsPerStep
        self.ymicronsPerStep = ymicronsPerStep
        return {"x":self.xmicronsPerStep,"y":self.ymicronsPerStep}

    def getPosUm(self) -> tuple:
        (xpossteps, ypossteps) = self._getPosSteps()
        xposmicrons = round(xpossteps*self.xmicronsPerStep)
        yposmicrons = round(ypossteps*self.ymicronsPerStep)

        if self.correctTwist:
            (xposmicrons, yposmicrons) = twist_corrector.stageToTrue(
                xposmicrons, 
                yposmicrons, 
                getCalibrationValue('stageTwist'), 
                getCalibrationValue('stageSkew'))

        return (xposmicrons, yposmicrons)

    def getVelocityMagnitude(self) -> tuple:
        def _getvelmag(address):
            v = self.motorClient.getVelocity(address)
            negV = np.iinfo('uint32').max + 1 - v
            return abs(negV)

        xvel = _getvelmag(self.xaddress)
        yvel = _getvelmag(self.yaddress)
        return (xvel, yvel)

    def getVelocity(self) -> tuple:
        def _getvel(address):
            v = self.motorClient.getVelocity(address)
            negV = np.iinfo('uint32').max + 1 - v
            isNeg = v > negV
            # the signs get flipped here because the motor
            # sends negative velocity when it is moving in
            # the positive direction
            return negV if isNeg else -v

        xvel = _getvel(self.xaddress)
        yvel = _getvel(self.yaddress)
        return (xvel, yvel)

    def getMotionStatus(self) -> dict:
        xstatus = self.motorClient.getMotionStatus(self.xaddress)
        ystatus = self.motorClient.getMotionStatus(self.yaddress)
        return {"x":xstatus, "y":ystatus}

    def getAlarm(self) -> dict:
        xalarm = self.motorClient.getAlarm(self.xaddress)
        yalarm = self.motorClient.getAlarm(self.yaddress)
        return {"x":xalarm, "y":yalarm}

    def clearAlarm(self) -> dict:
        xres = self.motorClient.clearAlarm(self.xaddress)
        yres = self.motorClient.clearAlarm(self.yaddress)
        return {"x":xres, "y":yres}

    def disable(self) -> dict:
        self._get_state_listener().disable()
        self.motorClient.setMotionDisabled(True)
        xres = self.motorClient.stop(self.xaddress)
        yres = self.motorClient.stop(self.yaddress)
        return {"x":xres, "y":yres}

    def enable(self) -> bool:
        self._get_state_listener().enable()
        self.motorClient.setMotionDisabled(False)
        return True

    def _setLowTorqueMode(self, lowTorqueMode:bool) -> bool:
        logger.info(f'setting low torque = {lowTorqueMode}')
        if lowTorqueMode:
            self._get_state_listener().low_torque_mode()
            self.motorClient.setPeakCurrent(self.xaddress, self.lowTorquePeakCurrent)
            self.motorClient.setPeakCurrent(self.yaddress, self.lowTorquePeakCurrent)
            self.motorClient.setClosedLoop(self.xaddress, 0)
            self.motorClient.setClosedLoop(self.yaddress, 0)
        else:
            self._get_state_listener().high_torque_mode()
            self.motorClient.setPeakCurrent(self.xaddress, self.highTorquePeakCurrent)
            self.motorClient.setPeakCurrent(self.yaddress, self.highTorquePeakCurrent)
            self.motorClient.setClosedLoop(self.xaddress, 2)
            self.motorClient.setClosedLoop(self.yaddress, 2)

        self.boardClient.setIsLowTorque(lowTorqueMode)

        return lowTorqueMode

    def _getLowTorqueMode(self) -> bool:
        xpc = self.motorClient.getPeakCurrent(self.xaddress)
        ypc = self.motorClient.getPeakCurrent(self.yaddress)
        xcl = self.motorClient.getClosedLoop(self.xaddress)
        ycl = self.motorClient.getClosedLoop(self.yaddress)
        logger.info(f'xpc: {xpc}, ypc: {ypc}, xcl: {xcl}, ycl: {ycl}')
        return (ypc == xpc == self.lowTorquePeakCurrent) and not xcl and not ycl

    def _setPosUm(self, xposition, yposition) -> tuple:

        if self.validateBounds:
            if not (0 <= xposition <= self.xlimitum) or \
                not (0 <= yposition <= self.ylimitum):
                logger.warn(f"Requested stage location ({xposition},{yposition}) is out of bounds.")
                return False

        if self.correctTwist:
            (xposition, yposition) = twist_corrector.trueToStage(
                xposition, 
                yposition, 
                getCalibrationValue('stageTwist'), 
                getCalibrationValue('stageSkew'))

        xpositionSteps = round(xposition / self.xmicronsPerStep)
        ypositionSteps = round(yposition / self.ymicronsPerStep)

        self._setPosSteps(xpositionSteps, ypositionSteps) 
        return (xposition, yposition)

    # never call this directly! only from _setPosUm()
    def _setPosSteps(self, xposition, yposition) -> bool:

        if self._getLowTorqueMode():
            vel = self.lowTorqueVel
            accel = self.lowTorqueAcc
            decel = self.lowTorqueDec
        else:
            vel = self.highTorqueVel
            accel = self.highTorqueAcc
            decel = self.highTorqueDec

        self.motorClient.setPosSteps(
            self.xaddress,
            int(np.uint32(xposition)),  #+ self.origin ? why not this
            vel,
            accel,
            decel, 
            0)
        self.motorClient.setPosSteps(
            self.yaddress,
            int(np.uint32(yposition)),  #+ self.origin ? why not this
            vel,
            accel,
            decel, 
            0)
        return True

    def _getPosSteps(self) -> tuple:
        xpos = np.uint32(self.motorClient.getPosSteps(self.xaddress)) - self.xorigin
        ypos = np.uint32(self.motorClient.getPosSteps(self.yaddress)) - self.yorigin
        return (int(xpos), int(ypos))

    def setPeakCurrent(self, t:int) -> int:
        self.motorClient.setPeakCurrent(self.xaddress, t)
        self.motorClient.setPeakCurrent(self.yaddress, t)
        return t

    def jogDown(self) -> bool:
        assert self.boardClient.getMonitorTrayPosition()
        self.motorClient.jog(self.yaddress, False)
        return True

    def jogUp(self) -> bool:
        assert self.boardClient.getMonitorTrayPosition()
        self.motorClient.jog(self.yaddress, True)
        return True

    def jogLeft(self) -> bool:
        assert self.boardClient.getMonitorTrayPosition()
        self.motorClient.jog(self.xaddress, False)
        return True

    def jogRight(self) -> bool:
        assert self.boardClient.getMonitorTrayPosition()
        self.motorClient.jog(self.xaddress, True)
        return True
