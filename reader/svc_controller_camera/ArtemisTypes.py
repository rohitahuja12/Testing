import ctypes as ct
import enum

ArtemisHandle = ct.POINTER(None)

class ArtemisError(enum.Enum):
    ARTEMIS_OK = 0
    ARTEMIS_INVALID_PARAMETER = 1
    ARTEMIS_NOT_CONNECTED = 2
    ARTEMIS_NOT_IMPLEMENTED = 3
    ARTEMIS_NO_RESPONSE = 4
    ARTEMIS_INVALID_FUNCTION = 5
    ARTEMIS_NOT_INITILIZED = 6
    ARTEMIS_OPERATION_FAILED = 7

class ArtemisCameraState(enum.Enum):
    CAMERA_ERROR = -1
    CAMERA_IDLE = 0
    CAMERA_WAITING = 1
    CAMERA_EXPOSING = 2
    CAMERA_READING = 3
    CAMERA_DOWNLOADING = 4
    CAMERA_FLUSHING = 5


class ArtemisProperties(ct.Structure):
    _fields_ = [
        ("Protocol", ct.c_int),
        ("nPixelsX", ct.c_int),
        ("nPixelsY", ct.c_int),
        ("PixelMicronsX", ct.c_float),
        ("PixelMicronsY", ct.c_float),
        ("ccdflags", ct.c_int),
        ("cameraFlags", ct.c_int),
        ("Description", ct.c_char*40),
        ("Manufacturer", ct.c_char*40)
    ]
