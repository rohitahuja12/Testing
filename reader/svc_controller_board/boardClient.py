import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
from lib_hardware_interface.client import InternalError
import eventLogging
import log
import glob
import pyudev
import serial
import time
from animation_frame import AnimationFrame
from enum import Enum
from animations.flash_red import flash_red
from animations.blue_breathe import blue_breathe
from animations.white_breathe import white_breathe
logger = log.getLogger("controller_board.boardClient")
event = eventLogging.get_event_logger(logger)

debug = False

DEV_ID_VENDOR = "2341"
DEV_ID_MODEL = "0042"


class BoardError(Enum):
    ERR_NONE = 0
    ERR_BAD_CMD=1             # the board was unable to interpret the command
    ERR_REJECTED_LOW_TORQUE=2 # rejected because the torque is set to low
    ERR_REJECTED_LID_OPEN=3   # rejected because the lid is open
    ERR_REJECTED_ASLEEP=4     # rejected because the reader is asleep
    ERR_REJECTED_PWR_OFF=5    # rejected because the main power is off
    ERR_EMERGENCY_PWR=6       # emergency occurred: power went off in high torque mode
    ERR_EMERGENCY_LID=7       # emergency occurred: lid opened in high torque mode
    ERR_EMERGENCY_TIMEOUT=8  
    ERR_EMERGENCY_TRAY_POS=9  # emergency occured: the tray tried to go to a position that is not allowed


class BoardClient():

    def __init__(self, idVendor=DEV_ID_VENDOR, idModel=DEV_ID_MODEL):
        event('EVENT_BOARD_INITIALIZING')

        self.encoding = 'utf-8'
        self.terminatingChar = '\t'
        self.responseDivisionChar = ':'
        self.baudRate = 115200
        self.responseTimeout = 5
        self.zStageHomed = False
        self.animations = [
            ("flash_red", flash_red),
            ("blue_breathe", blue_breathe),
            ("white_breathe", white_breathe)
        ]

        udevCtx = pyudev.Context()
        usbPaths = glob.glob('/dev/ttyACM*')
        logger.info(f'Searching for board on paths: {usbPaths}')
        for p in usbPaths:
            device = pyudev.Devices.from_device_file(udevCtx, p)
            vid = device.properties.get('ID_VENDOR_ID') 
            mid = device.properties.get('ID_MODEL_ID') 
            logger.info(f'Device at path {p} has vendorId "{vid}" and modelId "{mid}"')
            if vid == idVendor and mid == idModel:
                logger.info(f'Located board at path "{p}"')
                self.devicePath = p
                break
            else:
                logger.error('Unable to locate board.')

        assert self.devicePath
        self.device = serial.Serial(
            self.devicePath,
            self.baudRate,
            timeout = self.responseTimeout)
        
        do_reset = True # only in debug
        if do_reset:
            try:
                self.resetBoard()
            except:
                pass
        retries_before_reset = 15
        retry_ct = 0 
        while True:
            try:
                self.setIsLowTorque(True)
                self.clearButtonPressed()
                # self._loadAnimations()
                # self.startAnimation('blue_breathe')
                logger.info(f'Board startup complete.')
                event('EVENT_BOARD_CONTROLLER_INITIALIZED')
                return
            except Exception as e:
                logger.error(e)

                ++retry_ct
                if retry_ct == retries_before_reset:
                    logger.info('Resetting board in attempt to recover')
                    try:
                        self.resetBoard()
                    except Exception as e:
                        logger.error(e)
                    retry_ct = 0
                    time.sleep(10)

                else:
                    logger.info("Clearing error to attempt to proceed with board startup.")
                    try:
                        self.setEmergencyValue(0)
                    except Exception as e:
                        logger.error(e)

                time.sleep(1)

        raise Exception('Timed out waiting for board to handle requests.')


    def setMicronsPerStepZ(self, micronsPerStepZ:int) -> int:
        self.micronsPerStepZ = micronsPerStepZ
        return self.micronsPerStepZ

    def setMotorZLimitSteps(self, motorZLimitSteps:int) -> int:
        self.motorZLimitSteps = motorZLimitSteps
        return self.motorZLimitSteps

    def getMotorZLimitUm(self) -> int:
        return self.micronsPerStepZ * self.motorZLimitSteps

    def command(self, cmdStr:str) -> str:
        cmdRetryCt = 3
        res = None
        error = None
        for x in range(cmdRetryCt):
            try:
                self.device.write(bytes(cmdStr, self.encoding))
                res = self.device.read_until(
                    bytes(self.terminatingChar, self.encoding))
                res = str(res, self.encoding)
                t,err,data = res.replace('\t','').split(self.responseDivisionChar)
            except Exception as e:
                logger.error(f'errors....')
                logger.error(f'CMD IS "{cmdStr}" RESPONSE IS: "{res}"')
                raise InternalError(e, f'CMD IS "{cmdStr}" RESPONSE IS: "{res}"')

            if debug:
                logger.info(f'CMD IS "{cmdStr}" RESPONSE IS: "{res}"')

            error = int(err)

            if not error:
                return data
            else:
                continue

        raise Exception(BoardError(error))

    def getVersion(self) -> str:
        res = self.command('HQV000000.')
        return res

    def getSerialNumber(self) -> str:
        return self.command('HQN000000.')
        # return "4"
        
    def getIsAuxPowerOn(self) -> bool:
        return not int(self.command('HQW000000.'))

    def setIsAuxPowerOn(self, powerOn:bool) -> bool:
        flag = '0' if powerOn else '1'
        return not int(self.command(f'HCW00000{flag}.'))

    def getIsLowTorque(self) -> bool:
        return not not int(self.command('HQT000000.'))

    def setIsLowTorque(self, lowTorque:bool) -> bool:
        flag = '1' if lowTorque else '0'
        return not not int(self.command(f'HCT00000{flag}.'))

    def getEmergencyValue(self) -> int:
        return int(self.command('HQE000000.'))

    def setEmergencyValue(self, val:int) -> int:
        valStr = str(val).zfill(6)
        cmd=f'HCE{valStr}.'
        logger.info(cmd)
        return int(self.command(cmd))

    def getIsPowerOn(self) -> bool:
        return not not int(self.command('HQP000000.'))

    def getIsLidOpen(self) -> bool:
        return not not int(self.command('HQL000000.'))

    def resetBoard(self) -> str:
        return self.command('HCR000000.')

    def homeMotorZ(self) -> str:
        self.setIsAuxPowerOn(True)
        res = self.command('ZCH000000.')
        self.zStageHomed = True
        return res

    def getMotorZPositionUm(self) -> int:
        assert self.micronsPerStepZ
        assert self.motorZLimitSteps
        if not self.zStageHomed:
            self.homeMotorZ()
        return round(self._getMotorZPositionSteps() * self.micronsPerStepZ)

    def _getMotorZPositionSteps(self) -> int:
        if not self.zStageHomed:
            self.homeMotorZ()
        return int(self.command('ZQP000000.'))
    
    def setMotorZPositionUm(self, pos:int) -> int:
        assert self.micronsPerStepZ
        assert self.motorZLimitSteps
        if not self.zStageHomed:
            self.homeMotorZ()
        pos = round(pos / self.micronsPerStepZ)
        return self._setMotorZPositionSteps(pos)

    def _setMotorZPositionSteps(self, pos:int) -> int:
        if not self.zStageHomed:
            self.homeMotorZ()
        assert pos <= 5500 and pos >= 0
        posStr = str(pos).zfill(6)
        return self.command(f'ZCP{posStr}.')

    def getMotorZVelocity(self) -> int:
        return self.command('ZQV000000.')
    
    def setMotorZVelocity(self, vel:int) -> int:
        velStr = str(vel).zfill(6)
        return self.command(f'ZCV{velStr}.')

    def getMotorZAcceleration(self) -> int:
        return self.command('ZQA000000.')
    
    def setMotorZAcceleration(self, vel:int) -> int:
        velStr = str(vel).zfill(6)
        return self.command(f'ZCA{velStr}.')

    def getLaserAOn(self) -> bool:
        return not not int(self.command('AQO000000.'))
    
    def setLaserAOn(self, on:bool) -> bool:
        onStr = "I" if on else "O"
        return not not int(self.command(f'AC{onStr}000000.'))

    def getLaserBOn(self) -> bool:
        return not not int(self.command('BQO000000.'))
    
    def setLaserBOn(self, on:bool) -> bool:
        onStr = "I" if on else "O"
        return not not int(self.command(f'BC{onStr}000000.'))

    def getLaserDOn(self) -> bool:
        return not not int(self.command('DQO000000.'))
    
    def setLaserDOn(self, on:bool) -> bool:
        onStr = "I" if on else "O"
        return not not int(self.command(f'DC{onStr}000000.'))

    def setButtonColor(self, color:int) -> int:
        colorStr = str(color).zfill(6)
        return int(self.command(f'UCS{colorStr}.'))

    def getButtonColor(self) -> int:
        return int(self.command('UQS000000.'))

    def setRotatingDiffuserOn(self, on:bool) -> bool:
        onStr = "I" if on else "O"
        return not not int(self.command(f'RC{onStr}000000.'))
    
    def getRotatingDiffuserOn(self) -> bool:
        return not not int(self.command(f'RQI000000.'))

    def pressButton(self) -> bool:
        self.mockButtonPressed = True
        return self.mockButtonPressed
    
    def getButtonPressed(self) -> bool:
        return self.mockButtonPressed or self.command('UQE000000.') != "0"

    def clearButtonPressed(self) -> bool:
        self.mockButtonPressed = False
        return self.command('UCE000000.') != "0"

    def setMonitorTrayPosition(self, monitor:bool) -> bool:
        flag = '1' if monitor else '0'
        if not flag:
            e = self.getEmergencyValue()
            if e == 9:
                self.setEmergencyValue(0)
        return not not int(self.command(f'HCM00000{flag}.'))

    def getMonitorTrayPosition(self) -> bool:
        return not not int(self.command('HQM000000.'))

    # def startAnimation(self, animationName:str) -> int: 
        # animationIndex = next(
            # (i for i, e in enumerate(self.animations) if e[0] == animationName), 
            # -1)
        # return self.command(f'VCA{str(animationIndex).zfill(6)}.')

    # def getAnimationNames(self) -> str:
        # return [a[0] for a in self.animations]

    def _loadAnimations(self) -> int:
        logger.info('LOADING THOSE ANIMATIONS')

        # def _setFrame(frameindex, r, g, b):
            # logger.info(f'set frame, index:{frameindex}, red:{r}, green:{g}, blue:{b}')
            # self.command(f'FCE{str(frameindex).zfill(6)}.')
            # self.command(f'FCR{str(r).zfill(6)}.')
            # self.command(f'FCG{str(g).zfill(6)}.')
            # self.command(f'FCB{str(b).zfill(6)}.')

        # def _addFrameToAnim(animationIndex, animationFrameIndex, frameIndex, duration):
            # logger.info(f'add frame to anim: animIndex:{animationIndex}, animFrame:{animationFrameIndex}, frameIndex:{frameIndex}, duration:{duration}')
            # self.command(f'VCE{str(animationIndex).zfill(6)}.')
            # self.command(f'VCP{str(animationFrameIndex).zfill(6)}.')
            # self.command(f'VCF{str(frameIndex).zfill(6)}.')
            # self.command(f'VCD{str(duration).zfill(6)}.')

        # Create the animations 'bucket' on the board
        self.command(f'VCN{str(len(self.animations)).zfill(6)}.')

        for animIndex, anim in enumerate([a for a in self.animations[2:] if a]):

            animName, frames = anim

            # Create this animation and set length
            self.command(f'VCL00{str(animIndex).zfill(2)}{str(len(frames)).zfill(2)}.')

            for animationFrameIndex, frame in enumerate(frames):

                # Set frame color
                r = format(frame.red, '02x')
                g = format(frame.green, '02x')
                b = format(frame.blue, '02x')
                self.command(f'VCF{r}{g}{b}.')
                
                self.command(f'VCD')

                currentFrameIndex += 1

            lastIndex = len(anim)
            _addFrameToAnim(
                startingAnimationIndex + animIndex,
                lastIndex,
                255, # termination frame
                1)

        logger.info('LOADDED THOSE ANIMATIONS')
