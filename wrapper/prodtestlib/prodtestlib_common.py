"""Structs and constants used from prodtestlib_common.h file in prodtestlib.dll"""
from enum import Enum


class FPCErrorCode(Enum):
    """Python structure equivalent of fpc_error_code in prodtestlib.dll"""
    FPC_OK = 0
    FPC_PT_GENERAL_ERROR = 1
    FPC_UNDEFINED_SENSOR = 2
    FPC_WRONG_CHECKERBOARD_TYPE = 3
    FPC_IMAGE_QUALITY_SETTINGS_NOT_FOUND = 4
    FPC_INVALID_NUMBER_OF_LINES = 5
    FPC_IMAGE_QUALITY_ISSUE = 6
    FPC_PROBE_OUT_OF_RANGE = 7
    FPC_INCORRECT_VALUE = 8
    FPC_ADC_CRITERIA_FAILED = 9
    FPC_INPUT_PARAMETER_IS_NULL = 10
    FPC_PT_MALLOC_FAIL = 11
    FPC_PT_WRONG_INPUT_PARAMETER = 12
    FPC_PT_PIXEL_POSITION_OUTSIDE_MASKED_IMAGE = 13

    @classmethod
    def reverse_lookup(cls, value):
        """Returns error_name from value

        :param value: the integer value
        :type value: int
        :return: the error_name corresponding to the value
        :rtype: str
        """
        for _, member in cls.__members__.items():
            if member.value == value:
                return member
        raise LookupError

    @classmethod
    def errors(cls):
        """Returns a list of all error_names

        :return: list containing all member names
        :rtype: list of str
        """
        errs = []
        for _, member in cls.__members__.items():
            errs.append(member)
        return errs
