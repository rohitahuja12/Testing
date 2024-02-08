import RPi.GPIO as GPIO

class LaserManager():

    pinLaserOn = 17
    levelLaserOn = GPIO.HIGH
    levelLaserOff = GPIO.LOW
    stateLaserOn = False

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pinLaserOn,GPIO.OUT)
        GPIO.output(self.pinLaserOn,self.levelLaserOff)

    def setLaserOn(self, on:bool) -> bool:
        if on:
            GPIO.output(self.pinLaserOn,self.levelLaserOn)
        else:
            GPIO.output(self.pinLaserOn,self.levelLaserOff)
        self.stateLaserOn = on
        return self.stateLaserOn

    def getLaserOn(self) -> bool:
        return self.stateLaserOn