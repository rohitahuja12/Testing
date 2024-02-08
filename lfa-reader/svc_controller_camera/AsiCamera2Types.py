import ctypes as ct
import enum

AsiHandle = ct.POINTER(None)

class AsiBayerPattern(enum.Enum):
	ASI_BAYER_RG = 0
	ASI_BAYER_BG = 1
	ASI_BAYER_GR = 2
	ASI_BAYER_GB = 3

class AsiImgType(enum.Enum): # Supported Video Format 
	ASI_IMG_RAW8 = 0
	ASI_IMG_RGB24 = 1
	ASI_IMG_RAW16 = 2
	ASI_IMG_Y8 = 3
	ASI_IMG_END = -1

class AsiGuideDirection(enum.Enum): # Guider Direction
	ASI_GUIDE_NORTH = 0
	ASI_GUIDE_SOUTH = 1
	ASI_GUIDE_EAST = 2
	ASI_GUIDE_WEST = 3

class AsiFlipStatus(enum.Enum):
	ASI_FLIP_NONE = 0  # original
	ASI_FLIP_HORIZ = 1 # horizontal flip
	ASI_FLIP_VERT = 2  # vertical flip
	ASI_FLIP_BOTH = 3  # both horizontal and vertical flip

class AsiCameraMode(enum.Enum):
	ASI_MODE_NORMAL = 0
	ASI_MODE_TRIG_SOFT_EDGE = 1
	ASI_MODE_TRIG_RISE_EDGE = 2
	ASI_MODE_TRIG_FALL_EDGE = 3
	ASI_MODE_TRIG_SOFT_LEVEL = 4
	ASI_MODE_TRIG_HIGH_LEVEL = 5
	ASI_MODE_TRIG_LOW_LEVEL = 6
	ASI_MODE_END = -1

class AsiTriOutput(enum.Enum):
	ASI_TRIG_OUTPUT_PINA = 0 # Only Pin A output
	ASI_TRIG_OUTPUT_PINB = 1 # Only Pin B output
	ASI_TRIG_OUTPUT_NONE = -1

class AsiErrorCode(enum.Enum): # ASI ERROR CODE
	ASI_SUCCESS = 0
	ASI_ERROR_INVALID_INDEX = 1           # no camera connected or index value out of boundary
	ASI_ERROR_INVALID_ID = 2              # invalid ID
	ASI_ERROR_INVALID_CONTROL_TYPE = 3    # invalid control type
	ASI_ERROR_CAMERA_CLOSED = 4           # camera didn't open
	ASI_ERROR_CAMERA_REMOVED = 5          # failed to find the camera, maybe the camera has been removed
	ASI_ERROR_INVALID_PATH = 6            # cannot find the path of the file
	ASI_ERROR_INVALID_FILEFORMAT = 7 
	ASI_ERROR_INVALID_SIZE = 8            # wrong video format size
	ASI_ERROR_INVALID_IMGTYPE = 9         # unsupported image format
	ASI_ERROR_OUTOF_BOUNDARY = 10         # the startpos is out of boundary
	ASI_ERROR_TIMEOUT = 11                # timeout
	ASI_ERROR_INVALID_SEQUENCE = 12       # stop capture first
	ASI_ERROR_BUFFER_TOO_SMALL = 13       # buffer size is not big enough
	ASI_ERROR_VIDEO_MODE_ACTIVE = 14
	ASI_ERROR_EXPOSURE_IN_PROGRESS = 15
	ASI_ERROR_GENERAL_ERROR = 16          # general error, eg: value is out of valid range
	ASI_ERROR_INVALID_MODE = 17           # the current mode is wrong
	ASI_ERROR_GPS_NOT_SUPPORTED = 18      # this camera does not support GPS
	ASI_ERROR_GPS_VER_ERR = 19            # the FPGA GPS ver is too low
	ASI_ERROR_GPS_FPGA_ERR = 20           # failed to read or write data to FPGA
	ASI_ERROR_GPS_PARAM_OUT_OF_RANGE = 21 # start line or end line out of range, should make them between 0 ~ MaxHeight - 1
	ASI_ERROR_GPS_DATA_INVALID = 22       # GPS has not yet found the satellite or FPGA cannot read GPS data
	ASI_ERROR_END = 23

class AsiBool(enum.Enum):
	ASI_FALSE = 0
	ASI_TRUE = 1

class AsiCameraInfo(ct.Structure):
	_fields_ = [
		("Name", ct.c_char*64),					# the name of the camera, you can display this to the UI
		("CameraID", ct.c_int),					# this is used to control everything of the camera in other functions.Start from 0.
		("MaxHeight", ct.c_long),				# the max height of the camera
		("MaxWidth", ct.c_long),				# the max width of the camera
		("IsColorCam", ct.c_bool),
		("BayerPattern", ct.c_int),
		("SupportedBins", ct.c_int*16),			# 1 means bin1 which is supported by every camera, 2 means bin 2 etc.. 0 is the end of supported binning method
		("SupportedVideoFormat", ct.c_int*8),	# this array will content with the support output format type.IMG_END is the end of supported video format
		("PixelSize", ct.c_double),				# the pixel size of the camera, unit is um. such like 5.6um
		("MechanicalShutter", ct.c_bool),
		("ST4Port", ct.c_bool),
		("IsCoolerCam", ct.c_bool),
		("IsUSB3Host", ct.c_bool),
		("IsUSB3Camera", ct.c_bool),
		("ElecPerADU", ct.c_int32),
		("BitDepth", ct.c_int),
		("IsTriggerCam", ct.c_bool),
		("Unused", ct.c_char*16)
	]

class AsiControlType(enum.Enum): #Control type
	ASI_GAIN = 0
	ASI_EXPOSURE = 1
	ASI_GAMMA = 2
	ASI_WB_R = 3
	ASI_WB_B = 4
	ASI_OFFSET = 5
	ASI_BANDWIDTHOVERLOAD = 6	
	ASI_OVERCLOCK = 7
	ASI_TEMPERATURE = 8					# returns 10*temperature
	ASI_FLIP = 9
	ASI_AUTO_MAX_GAIN = 10
	ASI_AUTO_MAX_EXP = 11				# micro second
	ASI_AUTO_TARGET_BRIGHTNESS = 12 	# target brightness
	ASI_HARDWARE_BIN = 13
	ASI_HIGH_SPEED_MODE = 14
	ASI_COOLER_POWER_PERC = 15
	ASI_TARGET_TEMP = 16 				# does not need *10
	ASI_COOLER_ON = 17
	ASI_MONO_BIN = 18					# lead to less grid at software bin mode for color camera
	ASI_FAN_ON = 19
	ASI_PATTERN_ADJUST = 19
	ASI_ANTI_DEW_HEATER = 20
	ASI_FAN_ADJUST = 21
	ASI_PWRLED_BRIGNT = 22
	ASI_GPS_SUPPORT = 23
	ASI_GPS_START_LINE = 24
	ASI_GPS_END_LINE = 25
	ASI_ROLLING_INTERVAL = 26			# microsecond

class AsiControlCaps(ct.Structure):
	_fields_ = [
		("Name", ct.c_char*64),			# the name of the Control like Exposure, Gain etc..
		("Description", ct.c_char*128),	# description of this control 
		("MaxValue", ct.c_long),
		("MinValue", ct.c_long),
		("DefaultValue", ct.c_long),
		("IsAutoSupported", ct.c_bool),	# support auto set 1, don't support 0
		("IsWritable", ct.c_bool),		# some control like temperature can only be read by some cameras 
		("ControlType", ct.c_int),		# this is used to get value and set value of the control
		("Unused", ct.c_char*32)
	]

class AsiExposureStatus(enum.Enum):
	ASI_EXP_IDLE = 0	# idle states, you can start exposure now
	ASI_EXP_WORKING = 1	# exposing
	ASI_EXP_SUCCESS = 2	# exposure finished and waiting for download
	ASI_EXP_FAILED = 3	# exposure failed, you need to start exposure again

class AsiID(ct.Structure):
	_fields_ = [
		("id", ct.c_char*8)
	]

class AsiSupportedMode(ct.Structure):
	_fields_ = [
		("SupportedCameraMode", ct.c_int*16)	# this array will content with the support camera mode type.ASI_MODE_END is the end of supported camera mode
	]

class AsiDateTime(ct.Structure):
	_fields_ = [
		("Year", ct.c_int), 
		("Month", ct.c_int),
		("Day", ct.c_int),
		("Hour", ct.c_int),
		("Minute", ct.c_int),
		("Second", ct.c_int),
		("Msecond", ct.c_int),
		("Usecond", ct.c_int),		# Minimum Unit 0.1us, Maximum number 9999
		("Unused", ct.c_char*64)	# Using the Unused field to store concatenated strings
	]

# *** NOT IMPLEMENTED ***
#typedef struct _ASI_GPS_DATA {
#	ASI_DATE_TIME Datetime;
#	double Latitude;  // +: North Latitude -: South Latitude
#	double Longitude; // +: East longitude -: West longitude
#	int Altitude;     // Minimum Unit 0.1m, Maximum number 99999
#	int SatelliteNum; // Maximum number 99
#	char Unused[64];  
#} ASI_GPS_DATA;
