"""Structs and constants used from common_checkerboard.h file in prodtestlib.dll"""

import ctypes as c
from wrapper.fpc_c_core.fpc_sensor_info import DeadPixelsInfo


class FpcFrameFormat(c.Structure):
    """Equivalent to prodtestlib.dll's FpcFrameFormat"""
    _fields_ = [
        ("width", c.c_uint16),              # width in pixels, -1 indicates unknown value
        ("height", c.c_uint16),             # height in pixels, -1 indicates unknown value
        ("ppi", c.c_uint16),                # sampling intensity, -1 indicates unknown value
        ("bits_per_pixels", c.c_int8),      # Greyscale bit depth of the pixels, -1 indicates unknown value
        ("channels", c.c_int8),             # Number of channels
        ("greyscale_polarity", c.c_int8),   # 0 indicates that ridges are black, valleys are white,
                                            # 1 indicates the inverse situation , -1 indicates unknown value
        ("rotation", c.c_int8)              # orientation changes since the image was read measured in degrees
    ]

    def __init__(self, width, height):
        super(FpcFrameFormat, self).__init__()
        self.width = width
        self.height = height
        self.ppi = -1
        self.bits_per_pixels = 8
        self.channels = 1
        self.greyscale_polarity = -1
        self.rotation = 0


class FpcImage(c.Structure):
    """Equivalent to prodtestlib.dll's FpcImage"""
    _fields_ = [
        ("format", FpcFrameFormat),
        ("frame_count", c.c_uint16),
        ("buffer", c.POINTER(c.c_uint8)),
        ("capacity", c.c_uint32),
        ("dead_pixels_info", DeadPixelsInfo)    # Pixel position as layed out in memory.
    ]
