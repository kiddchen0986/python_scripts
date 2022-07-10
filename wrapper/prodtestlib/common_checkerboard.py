"""Structs and constants used from common_checkerboard.h file in prodtestlib.dll"""

from enum import Enum


class FpcCheckerboardT(Enum):
    """Python structure equivalent of fpc_checkerboard_t"""
    FPC_IMAGE_TEST_CHESS = 3
    FPC_IMAGE_TEST_CHESS_INV = 4
    FPC_IMAGE_TEST_WHITE = 5
    FPC_IMAGE_TEST_BLACK = 6


class FpcCheckerboardErrorTypeT(Enum):
    """Python structure equivalent of fpc_checkerboard_error_type_t"""
    FPC_TYPE1_MEDIAN_ERROR = 0x01
    FPC_TYPE2_MEDIAN_ERROR = 0x02
    FPC_NBR_DEAD_PIXEL_ERROR = 0x04
    FPC_NBR_DEAD_PIXEL_FD_ERROR = 0x08  # Nbr dead pixels in finger detect areas error
    FPC_HISTOGRAM_MEDIAN_ERROR = 0x10   # Used by gradient checkerboard
