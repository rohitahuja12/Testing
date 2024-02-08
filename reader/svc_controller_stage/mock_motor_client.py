import sys
sys.path.insert(0, './common')
from contextlib import contextmanager
from enum import Enum, Flag
from typing import List
import glob
import itertools
import log
import numpy as np
import threading

logger = log.getLogger("svc_controller_stage.mock_motor_client")

class StageClient():

    def __init__(self, idVendor=None, idModel=None):
        self.motionDisabled = False

    def setMotionDisabled(self, disabled):
        self.motionDisabled = disabled

    def getMotionDisabled(self):
        return self.motionDisabled

