import sys
sys.path.insert(0, './common')
from contextlib import contextmanager
from enum import Enum, Flag
from typing import List
import glob
import itertools
import log
import minimalmodbus as mb
import numpy as np
import pyudev
import serial
import threading

logger = log.getLogger("svc_controller_stage.motor_client")

def flatten(xs):
    return list(itertools.chain.from_iterable(xs))

def fromHex(x):
    return int.from_bytes(x, byteorder='big')

def intoNWords(N):
    return lambda x: [
        (x//pow(2,16*n))%pow(2,16*(n+1)) 
        for n in range(N-1,-1,-1)
    ]

def fromWords(words):
    return sum([w*pow(2,16*i) for i, w in enumerate(reversed(words))])

oneWord = intoNWords(1)
twoWords = intoNWords(2)

"""
CAurXYStage implementation
"""

class MotionStatus(Flag):
    FAULT = 0b1
    ENABLE = 0b10
    RUNNING = 0b100
    COMMAND_COMPLETED = 0b10000
    PATH_COMPLETED = 0b100000
    HOMING_COMPLETED = 0b1000000

class Alarm(Enum):
    NONE = 0x0
    OVER_CURRENT = 0x01
    OVER_VOLTAGE = 0x02
    CURRENT_SAMPLING_FAULT = 0x40
    FAILED_TO_LOCK_SHAFT = 0x80
    EEPROM_FAULT = 0x200
    AUTO_TUNING_FAULT = 0x100
    POSITION_FOLLOWING_ERROR = 0x20

DEV_ID_VENDOR = "0403"
DEV_ID_MODEL = "6001"


class StageClient():

    def __init__(self, idVendor=DEV_ID_VENDOR, idModel=DEV_ID_MODEL):
        udevCtx = pyudev.Context()
        usbPaths = glob.glob('/dev/ttyUSB*')
        logger.info(f'Searching for stage on paths: {usbPaths}')
        for p in usbPaths:
            device = pyudev.Devices.from_device_file(udevCtx, p)
            vid = device.properties.get('ID_VENDOR_ID') 
            mid = device.properties.get('ID_MODEL_ID') 
            logger.info(f'Device at path {p} has vendorId "{vid}" and modelId "{mid}"')
            if vid == idVendor and mid == idModel:
                logger.info(f'Located device at path "{p}"')
                self.devicePath = p
            else:
                logger.error('Unable to locate device.')

        assert self.devicePath

        # arg 2, slave address, provided arbitrarily here,
        # will be set at the beginning of each call
        self.stageDevice = mb.Instrument(self.devicePath, 1)
        self.stageDevice.mode = mb.MODE_RTU
        self.stageDevice.serial.baudrate=38400
        self.stageDevice.serial.bytesize=8
        self.stageDevice.serial.parity=serial.PARITY_NONE
        self.stageDevice.serial.stopbits=2
        self.stageDevice.serial.timeout=1
        self.motionDisabled = False

    def setMotionDisabled(self, disabled):
        self.motionDisabled = disabled

    def getMotionDisabled(self):
        return self.motionDisabled

    def sendStageHome(self, address):
        assert not self.motionDisabled
        self.stageDevice.address = address
        reg = fromHex(b'\x60\x02')
        val = fromHex(b'\x00\x20')
        self.stageDevice.write_register(reg, val, 0)

    def getPosSteps(self, address):
        self.stageDevice.address = address
        reg = fromHex(b'\x10\x12')
        results = self.stageDevice.read_registers(reg, 2)
        # combine registers into uint32
        result = (results[0] * 0x10000 + results[1])
        return result

    def getMotionStatus(self, address) -> List[MotionStatus]:
        self.stageDevice.address = address
        reg = fromHex(b'\x10\x03')
        result = self.stageDevice.read_register(reg, 0)
        flags = [flag.name for flag in MotionStatus if result & flag.value]
        return flags

    def getAlarm(self, address) -> Alarm:
        self.stageDevice.address = address
        reg = fromHex(b'\x22\x03')
        result = self.stageDevice.read_register(reg, 0)
        try:
            return Alarm(result)
        except:
            return result

    def clearAlarm(self, address):
        self.stageDevice.address = address
        reg = fromHex(b'\x18\x01')
        val = fromHex(b'\x11\x11')
        self.stageDevice.write_register(reg, val, 0)


    def setPosSteps(self, address, position, velocity, acceleration, deceleration, delayTime):
        assert not self.motionDisabled
        self.stageDevice.address = address
        register = fromHex(b'\x62\x00')
        mode = 1
        values = flatten([
            oneWord(mode),
            twoWords(position),
            oneWord(velocity),
            oneWord(acceleration),
            oneWord(deceleration),
            oneWord(delayTime),
            oneWord(16)
        ])
        self.stageDevice.write_registers(register, values)

    def stop(self, address):
        self.stageDevice.address = address
        reg = fromHex(b'\x60\x02')
        val = fromHex(b'\x00\x40')
        self.stageDevice.write_register(reg, val, 0)

    def getVelocity(self, address):
        self.stageDevice.address = address
        reg = fromHex(b'\x10\x46')
        results = self.stageDevice.read_registers(reg, 2)
        # combine registers into uint32
        result = (results[0] * 0x10000 + results[1])
        return result

    def setPeakCurrent(self, address, val):
        self.stageDevice.address = address
        reg = fromHex(b'\x01\x91')
        self.stageDevice.write_register(reg, val, 0)

    def getPeakCurrent(self, address):
        self.stageDevice.address = address
        reg = fromHex(b'\x01\x91')
        result = self.stageDevice.read_register(reg, 0)
        return result
        
    def setClosedLoop(self, address, isClosedLoop):
        self.stageDevice.address = address
        reg = fromHex(b'\x00\x03')
        self.stageDevice.write_register(reg, 2 if isClosedLoop else 0, 0)

    def getClosedLoop(self, address):
        self.stageDevice.address = address
        reg = fromHex(b'\x00\x03')
        result = self.stageDevice.read_register(reg, 0)
        return result == 2

    def setHomingHighVelocity(self, address, velocity):
        self.stageDevice.address = address
        reg = fromHex(b'\x60\x0F')
        self.stageDevice.write_register(reg, velocity, 0)

    def getHomingHighVelocity(self, address):
        self.stageDevice.address = address
        reg = fromHex(b'\x60\x0F')
        result = self.stageDevice.read_register(reg, 0)
        return result

    def setHomingAcc(self, address, acc):
        self.stageDevice.address = address
        reg = fromHex(b'\x60\x11')
        self.stageDevice.write_register(reg, acc, 0)

    def getHomingAcc(self, address):
        self.stageDevice.address = address
        reg = fromHex(b'\x60\x11')
        result = self.stageDevice.read_register(reg, 0)
        return result

    def setHomingDec(self, address, dec):
        self.stageDevice.address = address
        reg = fromHex(b'\x60\x12')
        self.stageDevice.write_register(reg, dec, 0)

    def getHomingDec(self, address):
        self.stageDevice.address = address
        reg = fromHex(b'\x60\x12')
        result = self.stageDevice.read_register(reg, 0)
        return result

    def setHomingLowVelocity(self, address, velocity):
        self.stageDevice.address = address
        reg = fromHex(b'\x60\x10')
        self.stageDevice.write_register(reg, velocity, 0)

    def getHomingLowVelocity(self, address):
        self.stageDevice.address = address
        reg = fromHex(b'\x60\x10')
        result = self.stageDevice.read_register(reg, 0)
        return result

    def setQuickStopTimeMs(self, address, time):
        self.stageDevice.address = address
        # reg = fromHex(b'\x60\x17')
        # self.stageDevice.write_register(reg, time, 0)
        # dev only, remove later
        reg = fromHex(b'\x60\x16')
        self.stageDevice.write_register(reg, time, 0)
        # end dev only, remove later

    def getQuickStopTimeMs(self, address):
        self.stageDevice.address = address
        reg = fromHex(b'\x60\x16')
        result = self.stageDevice.read_register(reg, 0)
        return result
    
    def jog(self, address:int, backward:bool) -> bool:#, velocity:int, acc_dec:int, interval:int, times:int)->bool:
        self.stageDevice.address = address

        velocity = 300
        register = fromHex(b'\x01\xE1')
        self.stageDevice.write_register(register, velocity, 0)

        interval = 50 
        register = fromHex(b'\x01\xE3')
        self.stageDevice.write_register(register, interval, 0)

        times = 500
        register = fromHex(b'\x01\xE5')
        self.stageDevice.write_register(register, times, 0)

        acc_dec = 50
        register = fromHex(b'\x01\xE7')
        self.stageDevice.write_register(register, acc_dec, 0)

        register = fromHex(b'\x18\x01')

        forward_dir = fromHex(b'\x40\x01')
        backward_dir = fromHex(b'\x40\x02')
        direction = backward_dir if backward else forward_dir
        self.stageDevice.write_register(register, direction, 0)

        return True
