import sys
sys.path.insert(0, './common')
sys.path.insert(0, './reader')
import eventLogging
import log
logger = log.getLogger("controller_board.mockBoardClient")
event = eventLogging.get_event_logger(logger)

class BoardClient():

    def __init__(self, idVendor=None, idModel=None):
        self.buttonPressed = False
        self.micronsPerStepZ = 0
        self.motorZLimitSteps = 0
        self.isAuxPowerOn = True
        self.isLidOpen = False
        self.laserAOn = False

    def getSerialNumber(self) -> str:
        return '4'

    def clearButtonPressed(self) -> bool:
        self.buttonPressed = False
        return self.buttonPressed

    def getButtonPressed(self) -> bool:
        return self.buttonPressed

    def setMicronsPerStepZ(self, micronsPerStepZ:int) -> int:
        self.micronsPerStepZ = micronsPerStepZ
        return self.micronsPerStepZ

    def setMotorZLimitSteps(self, motorZLimitSteps:int) -> int:
        self.motorZLimitSteps = motorZLimitSteps
        return self.motorZLimitSteps

    def getIsAuxPowerOn(self) -> bool:
        return self.isAuxPowerOn

    def setIsAuxPowerOn(self, powerOn:bool) -> bool:
        self.isAuxPowerOn = powerOn
        return self.isAuxPowerOn

    def getIsLidOpen(self) -> bool:
        return self.isLidOpen
      
    def setButtonColor(self, color:int) -> int:
        return 0
    
    def setMotorZPositionUm(self, pos:int) -> int:
        return pos
    
    def setLaserAOn(self, on:bool) -> bool:
        self.laserAOn = on
        return self.laserAOn

    # BEGIN mock methods that don't match the non-mock class

    def _setButtonPressed(self, pressed:bool) -> bool:
        event("EVENT_MAIN_BUTTON_PRESSED")
        self.buttonPressed = pressed
        return pressed

    def _setIsLidOpen(self, isOpen:bool) -> bool:
        self.isLidOpen = isOpen
        return self.isLidOpen


