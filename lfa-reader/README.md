To build this image on linux/amd64, you must have the QEMU container running.

`docker run --rm --privileged multiarch/qemu-user-static --reset -p yes`

Also, make sure that the camera library matches the system architecture (see ASI_Camera_SDK/ASI_linux_mac_SDK_Vx.xx/lib/README.txt):
x64 for 64-bit Ubuntu on Samsung laptop
arm8 for 64-bit OS on RPi4

The path specified in dockerfile for camera library location is given for RPi4

The path for the camera udev rules is system independent 