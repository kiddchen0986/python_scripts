"""reset_pixel.c python wrapper file for structs and functions, part of the prodtestlib.dll library."""

import ctypes as c

from utils.image import extract
from wrapper.fpc_c_core.fpc_image import FpcFrameFormat, FpcImage
from wrapper.fpc_c_core.fpc_sensor_info import DeadPixelsInfo
from wrapper.prodtestlib.prodtestlib_common import FPCErrorCode
from wrapper.wrapper_common import ErrorCode

"""ctypes types:
uint32_t    = c_uint32
uint16_t    = c_uint16
uint8_t     = c_uint8
bool        = c_bool
"""


class ResetPixelConfig(c.Structure):
    """Equivalent to prodtestlib.dll's reset_pixel_config_t"""
    _fields_ = [
        ("lower_limit_from_median", c.c_uint16),    # Lower than this, count as a reset pixel
        ("higher_limit_from_median", c.c_uint16),   # Higher than this, count as a reset pixel
        ("reset_error_upper_limit", c.c_uint16)     # Should be less than this value to pass
    ]


class ResetPixelsResult(c.Structure):
    """Equivalent to prodtestlib.dll's reset_pixels_result_t"""
    _fields_ = [
        ("median", c.c_uint8),
        ("pixels_outside_limit", c.c_uint16),
        ("pixels_under_limit", c.c_uint16),
        ("pixels_over_limit", c.c_uint16),
        ("min_value", c.c_uint16),
        ("max_value", c.c_uint16),
        ("pass", c.c_bool)
    ]

    def __init__(self):
        # A dictionary used to know for which values a histogram is interesting. The min and max values can be added if
        # a min and/or max line is wanted in the histogram. If a value is interesting together with another value, the
        # other value can be added to the list 'combine_figs'
        self.histogram = {"min_value": {"min": None,                # no min/max
                                        "max": None,
                                        "range": None,
                                        "combine_figs": [],         # no combined figures interesting
                                        "combine_figs_name": None
                                        },
                          "max_value": {"min": None,                # no min/max
                                        "max": None,
                                        "range": None,
                                        "combine_figs": [],
                                        "combine_figs_name": None}}  # no combined figures interesting

        # Initialize like normal
        super(ResetPixelsResult, self).__init__()


def init_reset_pixel_test(libc, test_package=None):
    """Prepares a config struct of type reset_pixel_config_t

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :return: test_package
    :rtype: dictionary
    """

    if test_package is None:
        test_package = {}

    test_package["config"] = ResetPixelConfig()
    # Fetch prodtestlib.dll function
    init_test = libc.init_reset_pixel_test
    # Assign the parameter types of the prodtestlib.dll function
    init_test.argtypes = [c.POINTER(ResetPixelConfig)]
    # Assign the return type of the prodtestlib.dll function
    init_test.restype = c.c_uint

    # Run the prodtestlib.dll function
    error_code = init_test(c.byref(test_package["config"]))

    # Fill test_package with remaining information
    if "dead_pixels_list" not in test_package:
        test_package["dead_pixels_list"] = DeadPixelsInfo()

    test_package["native_function"] = init_reset_pixel_test.__name__
    test_package["error_code"] = FPCErrorCode.reverse_lookup(error_code)

    return test_package


def reset_pixel_test(libc, image, test_package):
    """Runs the prodtestlib function reset_pixel_test

    :param libc: the c-library object used to retrieve the c-functions
    :type libc: c-library object
    :param image: the checkerboard image file path
    :type image: str
    :param test_package: dictionary containing config, result, error_code etc
    :type test_package: dictionary
    :return: test_package
    :rtype: dictionary
    """
    # If image file path not added to test_package; add it
    if "files" not in test_package:
        test_package["files"] = [image]

    # Prepare components for test
    test_package["result"] = ResetPixelsResult()
    image_data = extract(image)
    fpc_frame_format = FpcFrameFormat(width=image_data["width"], height=image_data["height"])
    fpc_image = FpcImage(format=fpc_frame_format,
                         frame_count=1,
                         buffer=image_data["buffer_p"],
                         capacity=image_data["capacity"],
                         dead_pixels_info=test_package["dead_pixels_list"])

    # If previous error, do not run test
    if not (test_package["error_code"] is FPCErrorCode.FPC_OK or ErrorCode.OK):
        return test_package

    # Retrieve test from prodtestlib and prepare it
    run_test = libc.reset_pixel_test
    run_test.argtypes = [c.POINTER(FpcImage),
                         c.POINTER(DeadPixelsInfo),
                         c.POINTER(ResetPixelConfig),
                         c.POINTER(ResetPixelsResult)]
    run_test.resttype = c.c_uint

    # Run test
    error_code = run_test(c.byref(fpc_image),
                          c.byref(test_package["dead_pixels_list"]),
                          c.byref(test_package["config"]),
                          c.byref(test_package["result"]))

    test_package["error_code"] = FPCErrorCode.reverse_lookup(error_code)
    test_package["native_function"] = reset_pixel_test.__name__
    return test_package
