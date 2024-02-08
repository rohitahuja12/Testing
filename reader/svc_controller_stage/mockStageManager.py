import sys
sys.path.insert(0, './common')
import eventLogging
import log
import numpy as np
import time
from threading import Thread
from motor_client import MotionStatus
from typing import Dict, List

logger = log.getLogger("svc_controller_stage.mockStageManager")
event = eventLogging.get_event_logger(logger)

class StageException(Exception):
    pass

class StageManager():

    def __init__( self, motorClient, boardClient, xaddress, yaddress):
        self.isMovingVal = False
        self.homed = True
        self.isEjected = False

    def _setReaderSettings( self, xmicronsPerStep, ymicronsPerStep, xbounds, ybounds) -> bool:
        return True 

    def isMoving(self) -> bool:
        return self.isMovingVal

    def getHomed(self) -> bool:
        return self.homed

    def getIsEjected(self) -> bool:
        return self.isEjected

    def eject(self) -> bool:
        event("EVENT_STAGE_EJECTING")
        self.isEjected = True
        return True

    def retract(self) -> bool:
        event("EVENT_STAGE_RETRACTING")
        self.isEjected = False
        return self.isEjected

    def _setHomed(self, homed:bool) -> bool:
        self.homed = homed
        return self.homed

    def _setIsMoving(self, isMoving:bool) -> bool:
        self.isMovingVal = isMoving
        return self.isMovingVal

    def _setIsEjected(self, isEjected:bool) -> bool:
        self.isEjected = isEjected
        return self.isEjected
    
    def setPosUm(self, xposition:int, yposition:int) -> tuple:
        event("EVENT_STAGE_MOVING")
        return (xposition, yposition)

