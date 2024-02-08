import sys
sys.path.insert(0, '.')
import core.logging.log as log
import os
from core.embedded.hardware_controller.synchronous_request.server import HardwareRequestServer
from core.embedded.hardware_controller.synchronous_request.command_table import CommandTable
from laser_manager import LaserManager

logger = log.getLogger("controller_laser.main")

requestTransport = os.environ['CONTROLLER_LASER_REQUEST_TRANSPORT']

def main():

    laserManager = LaserManager()

    HardwareRequestServer(
        requestTransport,
        CommandTable.fromObject(laserManager))


if __name__ == '__main__':
    main()
