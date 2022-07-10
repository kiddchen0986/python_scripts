""":mod:`wrapper_common` Common structs and functions used across the python wrapper files used to access the
prodtestlib.dll library."""

from enum import Enum, IntEnum

"""ctypes types:
uint32_t    = c_uint32
uint16_t    = c_uint16
uint8_t     = c_uint8
bool        = c_bool
"""


class CtypesEnum(IntEnum):
    """A ctypes-compatible IntEnum superclass. Never used directly"""
    @classmethod
    def from_param(cls, obj):
        return int(obj)


class ProdTestLib(Enum):
    """prodtestlib.dll function enum"""
    ADC_TEST = 0
    CALCULATE_BLOB = 1
    CALCULATE_CAPACITANCE = 2
    CALCULATE_CAPACITANCE2 = 3
    CHECKERBOARD_COMBINED_TEST = 4
    CHECKERBOARD_TEST = 5
    FREE_IMAGE_CONSTANT_MEDIANS = 6
    GET_CB_ERROR_CODE_DESCRIPTION = 7
    GET_ERROR_CODE_DESCRIPTION = 8
    GRADIENT_CHECKERBOARD_TEST = 9
    IMAGE_CONSTANT_TEST = 10
    INIT_BLOB_TEST = 11
    INIT_CHECKERBOARD_TEST = 12
    INIT_GRADIENT_CHECKERBOARD_TEST = 13
    INIT_GRADIENT_CHECKERBOARD_TEST_BASED_ON_TESTLEVEL = 14
    INIT_IMAGE_CONSTANT_TEST = 15
    INIT_IMAGE_QUALITY_TEST = 16
    INIT_PIXEL_CALIBRATION_TEST = 17
    INIT_RESET_PIXEL_TEST = 18
    PIXEL_CALIBRATION_TEST = 19
    PROD_TEST_IMAGE_QUALITY = 20
    RESET_PIXEL_TEST = 21


class ErrorCode(Enum):
    """Python script specific error codes enum"""
    OK = 0
    CONFIG_NOT_INITIALIZED = 1
    CSV_FILE_NOT_INITIALIZED = 2
    KEY_ERROR = 3
    TEST_PACKAGE_DOES_NOT_INCLUDE_PRODUCT_TYPE = 4
    PRODUCT_TYPE_WRONG_FORMAT = 5
    NO_CAPACITANCE_SETTINGS_FOUND_FOR_PRODUCT_TYPE = 6
    MTT_NOT_INITIALIZED = 7
    AREA_WIDTH_HEIGHT_ZERO = 8
