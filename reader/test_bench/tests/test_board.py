import sys
sys.path.insert(0, '.')
import unittest
from datetime import datetime, timedelta
from reader.lib_hardware_interface.client import HardwareClient
from reader.test_bench.action_player import Action, playNow
from threading import Event

class TestBoard(unittest.TestCase):

    def test_board_get_version(self):
        def do():
            client = HardwareClient('tcp://192.168.1.23:8120')
            x = client.getVersion()
            assert x == '2007'
        actions = [ Action(0, do) ]
        playNow(actions)

    def test_board_get_serial_number(self):
        def do():
            client = HardwareClient('tcp://192.168.1.23:8120')
            x = client.getSerialNumber()
            assert x == '4'
        actions = [ Action(0, do) ]
        playNow(actions)

    def test_board_get_set_aux_power(self):
        def setOn():
            client = HardwareClient('tcp://192.168.1.23:8120')
            client.setIsAuxPowerOn(True)
        def setOff():
            client = HardwareClient('tcp://192.168.1.23:8120')
            client.setIsAuxPowerOn(False)
        def assertOn():
            client = HardwareClient('tcp://192.168.1.23:8120')
            res = client.getIsAuxPowerOn()
            assert res == True
        def assertOff():
            client = HardwareClient('tcp://192.168.1.23:8120')
            res = client.getIsAuxPowerOn()
            assert res == False

        actions = [ 
           Action(0, setOn),
           Action(0, assertOn),
           Action(0, setOff),
           Action(0, assertOff),
           Action(0, setOn),
           Action(0, assertOn),
           Action(0, setOff),
           Action(0, assertOff)
        ]
        playNow(actions, max_workers=1)

    def test_board_get_set_low_torque(self):
        def setOn():
            client = HardwareClient('tcp://192.168.1.23:8120')
            client.setIsLowTorque(True)
        def setOff():
            client = HardwareClient('tcp://192.168.1.23:8120')
            client.setIsLowTorque(False)
        def assertOn():
            client = HardwareClient('tcp://192.168.1.23:8120')
            res = client.getIsLowTorque()
            assert res == True
        def assertOff():
            client = HardwareClient('tcp://192.168.1.23:8120')
            res = client.getIsLowTorque()
            assert res == False

        actions = [ 
           Action(0, setOn),
           Action(0, assertOn),
           Action(0, setOff),
           Action(0, assertOff),
           Action(0, setOn),
           Action(0, assertOn),
           Action(0, setOff),
           Action(0, assertOff)
        ]
        playNow(actions, max_workers=1)

    def test_board_moves_z(self):
        def scoot_z():
            client = HardwareClient('tcp://192.168.1.23:8120')
            pos = client.getMotorZPositionUm()
            print(f'MOTOR Z : {pos}')
            # client.setMotorZPositionUm()
        actions = [ 
           Action(0, scoot_z)
        ]
        playNow(actions, max_workers=1)



if __name__ == "__main__":
    unittest.main()
